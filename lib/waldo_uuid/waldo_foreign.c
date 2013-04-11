#include <stdio.h>
#include <inttypes.h>
#include <uuid/uuid.h>

//unnecessary to have .h file
void foreign_uuid_two_unsigned_longs(
    uint64_t* high_order_bits, uint64_t* low_order_bits)
{
    *high_order_bits = 0;
    *low_order_bits = 0;

    uuid_t u;
    uuid_generate_random(u);

    *high_order_bits += ((uint64_t)u[0]);
    *high_order_bits += ((uint64_t)u[1]) << 8;
    *high_order_bits += ((uint64_t)u[2]) << 16;
    *high_order_bits += ((uint64_t)u[3]) << 24;
    *high_order_bits += ((uint64_t)u[4]) << 32;
    *high_order_bits += ((uint64_t)u[5]) << 40;
    *high_order_bits += ((uint64_t)u[6]) << 48;    
    *high_order_bits += ((uint64_t)u[7]) << 56;

    *low_order_bits += ((uint64_t)u[8]);
    *low_order_bits += ((uint64_t)u[9]) << 8;
    *low_order_bits += ((uint64_t)u[10]) << 16;
    *low_order_bits += ((uint64_t)u[11]) << 24;
    *low_order_bits += ((uint64_t)u[12]) << 32;
    *low_order_bits += ((uint64_t)u[13]) << 40;
    *low_order_bits += ((uint64_t)u[14]) << 48;    
    *low_order_bits += ((uint64_t)u[15]) << 56;
}
