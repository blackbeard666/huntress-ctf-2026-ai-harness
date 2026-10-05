# Chunk Norris — notes
- hypothesis: png.ihdr_dimensions_pixels = IHDR width x height | IHDR @0x10: 0x10d x 0x99 = 269x153; chunks IHDR,IDAT,IEND, CRCs ok; inflated IDAT 123624 == 153*(1+269*3) (geometry consistent, no passenger in panel-001) | form follows Day-4 jpeg.sof_dimensions_pixels '<w>x<h>'
- submit 269x153 | CORRECT (flag 5a15c306462385a6185389f75bdab0d9)
- solver: solver/solve.py walks chunks by declared length; solver-test ok, solver-run ok; synthetic mastery-shaped variant (set1/set2, -01/-02 zips, ruSt chunk, data after IEND) ok
