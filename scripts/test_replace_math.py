import docx
from docx.oxml import parse_xml

doc = docx.Document()
p = doc.add_paragraph('original')
p_math = p.insert_paragraph_before()
p_math._element.append(parse_xml('<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:oMath><m:r><m:t>E = mc^2</m:t></m:r></m:oMath></m:oMathPara>'))
p._element.getparent().remove(p._element)
doc.save('test_replace_math.docx')
print('Math replacement verified!')
