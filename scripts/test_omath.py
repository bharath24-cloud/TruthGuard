import docx
from docx.oxml import parse_xml

doc = docx.Document()
p = doc.add_paragraph()
omath_xml = '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:oMath><m:r><m:t>R_contra = </m:t></m:r><m:f><m:num><m:r><m:t>N_contradicted</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_verifiable)</m:t></m:r></m:den></m:f></m:oMath></m:oMathPara>'
element = parse_xml(omath_xml)
p._element.append(element)
doc.save('test_math.docx')
print('Successfully saved docx with native oMath!')
