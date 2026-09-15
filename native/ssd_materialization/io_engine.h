#pragma once
#include <cstdint>
#include <string>
#include <map>
#include <complex>
using Complex=std::complex<double>;
static_assert(sizeof(Complex)==16, "complex128 layout required");
struct Buffer {
    Complex* data=nullptr;
    explicit Buffer(uint64_t bytes);
    ~Buffer();
    Buffer(const Buffer&)=delete;
};
struct IO {
    bool direct=false;
    uint64_t read_bytes=0,write_bytes=0,reads=0,writes=0;
    void read(int fd,void* buf,uint64_t bytes,uint64_t offset);
    void write(int fd,const void* buf,uint64_t bytes,uint64_t offset);
};
struct File {
    int fd=-1;
    File(const std::string& path,bool output,bool direct);
    ~File();
    File(const File&)=delete;
};
void require(bool condition,const std::string& message);
void syscheck(bool condition,const std::string& message);
uint64_t state_bytes(int q);
uint64_t allocated_bytes(int fd);
uint64_t file_size(int fd);
double seconds();
double sync_file(int fd);
std::map<std::string,uint64_t> process_io();
std::map<std::string,uint64_t> device_io(const std::string& path);
double random_component(uint64_t index,uint64_t seed);
