# ufo-upiv
upiv code using ufo framework

## How to use
1. Install ufo-core and ufo-filters from https://github.com/ufo-kit
2. Compile filters
  * mkdir build; cd build/
  * cmake ..
  * make; make install
3. source filters/SourceMe.sh

## Notice

* Dir filters/ contains the filters made for upiv project. Therefore the ufo framework need to know where to look for these filters. To set customized path for filters,  a special patch for ufo-core is needed.
