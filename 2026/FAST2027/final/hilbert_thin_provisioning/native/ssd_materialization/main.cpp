#include "io_engine.h"
#include "gate_kernels.h"
#include <sys/resource.h>
#include <unistd.h>
#include <fcntl.h>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <algorithm>
#include <cstring>
#include <set>
#include <cmath>
static double cpu(){struct rusage r{};getrusage(RUSAGE_SELF,&r);return r.ru_utime.tv_sec+r.ru_utime.tv_usec*1e-6+r.ru_stime.tv_sec+r.ru_stime.tv_usec*1e-6;}
static void emit_delta(const std::string& prefix,const std::map<std::string,uint64_t>& before,const std::map<std::string,uint64_t>& after,
                       const std::initializer_list<std::string>& keys){
    for(const auto& k:keys){std::cout<<",\""<<prefix<<k<<"\":";
        if(before.count(k)&&after.count(k)&&after.at(k)>=before.at(k))std::cout<<after.at(k)-before.at(k);else std::cout<<"null";}
}
int main(int argc,char** argv){try{
    std::map<std::string,std::string> a;
    require(argc%2==1,"arguments must be --key value pairs");
    for(int i=1;i<argc;i+=2){require(std::string(argv[i]).rfind("--",0)==0,"invalid argument");a[argv[i]+2]=argv[i+1];}
    auto get=[&](const std::string& k,const std::string& d=""){return a.count(k)?a.at(k):d;};
    std::string action=get("action","run"),mode=get("mode","buffered");
    require(mode=="direct"||mode=="buffered","invalid I/O mode");bool direct=mode=="direct";
    if(action=="probe"){
        File f(get("output"),true,true);Buffer b(4096);std::memset(static_cast<void*>(b.data),0x5a,4096);IO io;io.direct=true;
        io.write(f.fd,b.data,4096,0);sync_file(f.fd);std::memset(static_cast<void*>(b.data),0,4096);io.read(f.fd,b.data,4096,0);
        require(reinterpret_cast<unsigned char*>(b.data)[4095]==0x5a,"direct probe mismatch");
        std::cout<<"{\"direct_io_supported\":true,\"alignment\":4096}\n";return 0;
    }
    int q=std::stoi(get("q","-1"));uint64_t bytes=state_bytes(q);
    uint64_t configured=std::stoull(get("chunk-bytes","16777216"));
    require(configured>=4096&&configured<=64ULL*1024*1024&&(configured&(configured-1))==0,"invalid chunk size");
    uint64_t chunk=std::min(configured,bytes),count=chunk/16;
    require(4*chunk<=256ULL*1024*1024,"working buffers exceed 256 MiB");
    if(direct)require(chunk%4096==0,"state too small for aligned DIRECT I/O");
    IO io;io.direct=direct;
    if(action=="generate"){
        File f(get("output"),true,direct);Buffer b(chunk);uint64_t seed=std::stoull(get("seed","20260916"));
        syscheck(ftruncate(f.fd,bytes)==0,"ftruncate input");
        for(uint64_t off=0;off<bytes;off+=chunk){for(uint64_t i=0;i<count;++i){uint64_t j=off/16+i;b.data[i]={random_component(2*j,seed),random_component(2*j+1,seed)};}io.write(f.fd,b.data,chunk,off);}
        sync_file(f.fd);int advice=posix_fadvise(f.fd,0,0,POSIX_FADV_DONTNEED);
        std::cout<<"{\"bytes\":"<<bytes<<",\"seed\":"<<seed<<",\"generation_id\":\"splitmix64-index-v1\",\"fadvise_rc\":"<<advice<<"}\n";return 0;
    }
    require(action=="run","invalid action");
    const std::set<std::string> policies={"NAIVE_BASIS","THIN_BASIS","FUSED_BASIS","NAIVE_PRODUCT","PRODUCT_FUSED"};
    std::string policy=get("policy"),gate=get("gate");require(policies.count(policy),"invalid policy");
    require(gate=="cx_product_control"||gate=="cx_product_target"||gate=="cz"||gate=="generic","invalid gate");
    int target=std::stoi(get("target","3"));require(target>=0&&target<q&&(2ULL<<target)<=count,"target pair must fit inside aligned chunk");
    Complex alpha(std::stod(get("ar","0.7071067811865475244")),std::stod(get("ai","0")));
    Complex beta(std::stod(get("br","0.7071067811865475244")),std::stod(get("bi","0")));
    require(std::isfinite(std::norm(alpha)+std::norm(beta))&&std::abs(std::norm(alpha)+std::norm(beta)-1)<1e-12,"product state not normalized");
    bool basis=policy.find("BASIS")!=std::string::npos;
    if(basis)require(std::norm(alpha)<1e-24||std::norm(beta)<1e-24,"BASIS requires a known basis state");
    Matrix matrix{};
    if(gate=="generic"){std::ifstream f(get("matrix"),std::ios::binary);f.read(reinterpret_cast<char*>(matrix.data()),sizeof(matrix));
        require(f.gcount()==sizeof(matrix)&&f.peek()==EOF,"generic matrix must contain exactly 16 complex128 entries");
        for(int i=0;i<4;++i)for(int j=0;j<4;++j){Complex v=0.;for(int k=0;k<4;++k)v+=std::conj(matrix[k*4+i])*matrix[k*4+j];require(std::abs(v-(i==j?1.:0.))<1e-10,"matrix is not unitary");}}
    File input(get("input"),false,direct);require(file_size(input.fd)==bytes,"input file size mismatch");
    File output(get("output"),true,direct);Buffer x0(chunk),x1(chunk),y0(chunk),y1(chunk);
    int advice=posix_fadvise(input.fd,0,0,POSIX_FADV_DONTNEED),intermediate_advice=0;
    auto proc0=process_io(),dev0=device_io(get("device-stat"));double cpu0=cpu(),start=seconds(),sync=0.;
    syscheck(ftruncate(output.fd,2*bytes)==0,"ftruncate output");
    bool is_fused=policy=="PRODUCT_FUSED"||policy=="FUSED_BASIS";
    uint64_t before_gate=allocated_bytes(output.fd);
    if(!is_fused){
        for(uint64_t off=0;off<bytes;off+=chunk){io.read(input.fd,x0.data,chunk,off);
            for(uint64_t i=0;i<count;++i){y0.data[i]=alpha*x0.data[i];y1.data[i]=beta*x0.data[i];}
            if(policy!="THIN_BASIS"||std::norm(alpha)>0)io.write(output.fd,y0.data,chunk,off);
            if(policy!="THIN_BASIS"||std::norm(beta)>0)io.write(output.fd,y1.data,chunk,bytes+off);
        }
        sync+=sync_file(output.fd);before_gate=allocated_bytes(output.fd);
        intermediate_advice=posix_fadvise(output.fd,0,0,POSIX_FADV_DONTNEED);
    }
    for(uint64_t off=0;off<bytes;off+=chunk){
        if(is_fused){io.read(input.fd,x0.data,chunk,off);fused(x0.data,y0.data,y1.data,count,target,alpha,beta,gate,matrix);}
        else{io.read(output.fd,x0.data,chunk,off);io.read(output.fd,x1.data,chunk,bytes+off);transform(x0.data,x1.data,y0.data,y1.data,count,target,gate,matrix);}
        io.write(output.fd,y0.data,chunk,off);io.write(output.fd,y1.data,chunk,bytes+off);
    }
    sync+=sync_file(output.fd);double elapsed=seconds()-start,cpu_elapsed=cpu()-cpu0;
    auto proc1=process_io(),dev1=device_io(get("device-stat"));struct rusage usage{};getrusage(RUSAGE_SELF,&usage);
    std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"io_mode\":\""<<mode<<"\",\"policy\":\""<<policy<<"\",\"gate\":\""<<gate
        <<"\",\"q_old\":"<<q<<",\"q_new\":"<<q+1<<",\"old_state_bytes\":"<<bytes<<",\"new_state_bytes\":"<<2*bytes
        <<",\"chunk_bytes\":"<<configured<<",\"effective_chunk_bytes\":"<<chunk<<",\"target\":"<<target
        <<",\"algorithmic_read_bytes\":"<<io.read_bytes<<",\"algorithmic_write_bytes\":"<<io.write_bytes
        <<",\"user_bytes_read\":"<<io.read_bytes<<",\"user_bytes_written\":"<<io.write_bytes
        <<",\"pread_calls\":"<<io.reads<<",\"pwrite_calls\":"<<io.writes
        <<",\"operation_elapsed_s\":"<<elapsed-sync<<",\"sync_elapsed_s\":"<<sync<<",\"total_elapsed_s\":"<<elapsed
        <<",\"operation_plus_sync_elapsed_s\":"<<elapsed<<",\"cpu_elapsed_s\":"<<cpu_elapsed
        <<",\"effective_input_GBps\":"<<bytes/elapsed/1e9<<",\"effective_output_GBps\":"<<2*bytes/elapsed/1e9
        <<",\"logical_output_bytes\":"<<file_size(output.fd)<<",\"allocated_output_bytes_before_gate\":"<<before_gate
        <<",\"allocated_output_bytes_after_gate\":"<<allocated_bytes(output.fd)<<",\"peak_rss_bytes\":"<<usage.ru_maxrss*1024ULL
        <<",\"configured_buffer_bytes\":"<<4*chunk<<",\"fadvise_rc\":"<<advice<<",\"intermediate_fadvise_rc\":"<<intermediate_advice;
    emit_delta("proc_",proc0,proc1,{"rchar","wchar","read_bytes","write_bytes","cancelled_write_bytes"});
    emit_delta("device_",dev0,dev1,{"sectors_read","sectors_written","read_bytes","write_bytes"});
    std::cout<<"}\n";
    return 0;
}catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 2;}}
