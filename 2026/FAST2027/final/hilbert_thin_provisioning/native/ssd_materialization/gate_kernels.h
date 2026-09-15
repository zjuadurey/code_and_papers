#pragma once
#include "io_engine.h"
#include <array>
using Matrix=std::array<Complex,16>;
void transform(const Complex* x0,const Complex* x1,Complex* y0,Complex* y1,uint64_t count,int target,
               const std::string& gate,const Matrix& u);
void fused(const Complex* x,Complex* y0,Complex* y1,uint64_t count,int target,
           Complex alpha,Complex beta,const std::string& gate,const Matrix& u);
