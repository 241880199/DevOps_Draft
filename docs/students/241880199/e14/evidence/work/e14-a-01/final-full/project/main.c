#include <stdio.h>
#include "config.h"
int helper(void);
/* 输出配置值，供构建和增量验证使用。 */
int main(void){printf("%d\n",VALUE+helper());return 0;}
