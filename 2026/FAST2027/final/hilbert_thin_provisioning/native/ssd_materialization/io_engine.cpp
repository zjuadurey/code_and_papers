#include "io_engine.h"
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <cerrno>
#include <cstring>
#include <cstdlib>
#include <stdexcept>
#include <chrono>
#include <fstream>
#include <vector>
#include <limits>
#include <new>
void require(bool c,const std::string& m){if(!c)throw std::runtime_error(m);}
void syscheck(bool c,const std::string& m){if(!c)throw std::runtime_error(m+": "+std::strerror(errno));}
Buffer::Buffer(uint64_t bytes){require(bytes>0&&bytes<=64ULL*1024*1024,"buffer exceeds 64 MiB limit");
    int rc=posix_memalign(reinterpret_cast<void**>(&data),4096,bytes);require(rc==0,"posix_memalign failed");
    require(reinterpret_cast<uintptr_t>(data)%4096==0,"buffer alignment failure");
    for(uint64_t i=0;i<bytes/sizeof(Complex);++i)new(data+i) Complex();}
Buffer::~Buffer(){free(data);}
File::File(const std::string& path,bool output,bool direct){
    require(path.rfind("/dev/",0)!=0,"Device paths are forbidden");
    int flags=output?(O_RDWR|O_CREAT|O_EXCL):O_RDONLY;
    fd=open(path.c_str(),flags|O_CLOEXEC|O_NOFOLLOW|(direct?O_DIRECT:0),0600);
    syscheck(fd>=0,"open regular file "+path);
    struct stat st{};syscheck(fstat(fd,&st)==0,"fstat");require(S_ISREG(st.st_mode),"Only ordinary regular files permitted");
}
File::~File(){if(fd>=0)close(fd);}
static void alignment(bool direct,const void* buf,uint64_t bytes,uint64_t offset){
    if(direct)require(reinterpret_cast<uintptr_t>(buf)%4096==0&&bytes%4096==0&&offset%4096==0,"O_DIRECT alignment failure");
}
void IO::read(int fd,void* buf,uint64_t bytes,uint64_t offset){
    alignment(direct,buf,bytes,offset);
    ssize_t got;do{got=pread(fd,buf,bytes,static_cast<off_t>(offset));}while(got<0&&errno==EINTR);
    syscheck(got>=0,"pread");require(static_cast<uint64_t>(got)==bytes,"short pread");read_bytes+=bytes;++reads;
}
void IO::write(int fd,const void* buf,uint64_t bytes,uint64_t offset){
    alignment(direct,buf,bytes,offset);
    ssize_t got;do{got=pwrite(fd,buf,bytes,static_cast<off_t>(offset));}while(got<0&&errno==EINTR);
    syscheck(got>=0,"pwrite (including ENOSPC)");require(static_cast<uint64_t>(got)==bytes,"short pwrite");write_bytes+=bytes;++writes;
}
uint64_t state_bytes(int q){require(q>=1&&q<=40,"invalid q; supported 1..40");
    uint64_t b=16ULL<<q;require(b<=static_cast<uint64_t>(std::numeric_limits<off_t>::max())/2,"state offset overflow");return b;}
uint64_t file_size(int fd){struct stat st{};syscheck(fstat(fd,&st)==0,"fstat");return st.st_size;}
uint64_t allocated_bytes(int fd){struct stat st{};syscheck(fstat(fd,&st)==0,"fstat blocks");return st.st_blocks*512ULL;}
double seconds(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
double sync_file(int fd){double start=seconds();syscheck(fdatasync(fd)==0,"fdatasync");return seconds()-start;}
std::map<std::string,uint64_t> process_io(){std::ifstream f("/proc/self/io");std::string k;uint64_t v;std::map<std::string,uint64_t> result;
    while(f>>k>>v){if(k.back()==':')k.pop_back();result[k]=v;}return result;}
std::map<std::string,uint64_t> device_io(const std::string& path){
    if(path.empty())return {};
    require(path.rfind("/sys/class/block/",0)==0&&path.size()>5&&path.substr(path.size()-5)=="/stat","invalid device counter path");
    std::ifstream f(path);std::vector<uint64_t> a;uint64_t v;while(f>>v)a.push_back(v);
    if(a.size()<7)return {};
    return {{"sectors_read",a[2]},{"sectors_written",a[6]},{"read_bytes",a[2]*512},{"write_bytes",a[6]*512}};
}
double random_component(uint64_t index,uint64_t seed){
    uint64_t z=index+seed+0x9e3779b97f4a7c15ULL;
    z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;z^=z>>31;
    return static_cast<double>(z>>11)*0x1.0p-53-.5;
}
