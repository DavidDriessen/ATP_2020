
spirit_obj = "Spirit:\
  push {r7, lr}\
  sub sp, sp, #8\
  add r7, sp, #0\
  str r0, [r7, #4]\
  ldr r3, [r7, #4]\
  movs r2, #0\
  str r2, [r3]\
  ldr r3, [r7, #4]\
  adds r3, r3, #4\
  movs r2, #254\
Spirit_3:\
  cmp r2, #0\
  blt Spirit_2\
  movs r1, #0\
  str r1, [r3]\
  adds r3, r3, #4\
  subs r2, r2, #1\
  b Spirit_3\
Spirit_2:\
  ldr r2, [r7, #4]\
  movs r3, #128\
  lsls r3, r3, #3\
  movs r1, #0\
  strb r1, [r2, r3]\
  ldr r3, [r7, #4]\
  ldr r2, summon_1\
  movs r1, #0\
  str r1, [r3, r2]\
  ldr r3, [r7, #4]\
  movs r0, r3\
  mov sp, r7\
  add sp, sp, #8\
  pop {r7, pc}"

summon_helper = "\
summon:\
  push {r7, lr}\
  sub sp, sp, #16\
  add r7, sp, #0\
  str r0, [r7, #4]\
  movs r3, #0\
  str r3, [r7, #12]\
summon_1:\
  ldr r3, [r7, #12]\
  adds r3, r3, #1\
  str r3, [r7, #12]\
  ldr r3, [r7, #4]\
  ldr r3, [r3]\
  movs r2, #1\
  adds r1, r2, #0\
  ldr r2, [r7, #12]\
  cmp r2, r3\
  bgt Spirit_2\
  movs r3, #0\
  adds r1, r3, #0\
Spirit_2:\
  uxtb r3, r1\
  cmp r3, #0\
  beq Spirit_3\
  movs r3, #0\
  str r3, [r7, #12]\
Spirit_3:\
  ldr r2, [r7, #4]\
  ldr r3, [r7, #12]\
  lsls r3, r3, #2\
  adds r3, r2, r3\
  adds r3, r3, #4\
  ldr r3, [r3]\
  ldr r2, [r7, #4]\
  movs r0, r2\
  blx r3\
  ldr r2, [r7, #4]\
  movs r3, #128\
  lsls r3, r3, #3\
  ldrb r3, [r2, r3]\
  cmp r3, #0\
  bne summon_2\
  b summon_1\
summon_2:\
  nop\
  mov sp, r7\
  add sp, sp, #16\
  pop {r7, pc}"