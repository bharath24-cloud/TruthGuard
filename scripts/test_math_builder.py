import docx
from docx.oxml import parse_xml

doc = docx.Document()

# Equation 1: L2 Normalization
xml1 = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:r><m:t>q̂ = </m:t></m:r>'
    '<m:f><m:num><m:r><m:t>q</m:t></m:r></m:num><m:den><m:r><m:t>‖q‖₂</m:t></m:r></m:den></m:f>'
    '<m:r><m:t>,   v̂ = </m:t></m:r>'
    '<m:f><m:num><m:r><m:t>v</m:t></m:r></m:num><m:den><m:r><m:t>‖v‖₂</m:t></m:r></m:den></m:f>'
    '</m:oMath>'
    '</m:oMathPara>'
)

# Equation 2: Sim / Cosine
xml2 = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:r><m:t>sim(q, v) = q̂ · v̂ = cos(θ)</m:t></m:r>'
    '</m:oMath>'
    '</m:oMathPara>'
)

# Equation 3: Softmax
xml3 = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:r><m:t>P(labelᵢ | c, p) = </m:t></m:r>'
    '<m:f><m:num><m:r><m:t>exp(zᵢ)</m:t></m:r></m:num><m:den><m:r><m:t>∑ⱼ exp(zⱼ)</m:t></m:r></m:den></m:f>'
    '</m:oMath>'
    '</m:oMathPara>'
)

# Equation 4: Contradiction Rate
xml4 = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:r><m:t>R_contra = </m:t></m:r>'
    '<m:f><m:num><m:r><m:t>N_contradicted</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_verifiable)</m:t></m:r></m:den></m:f>'
    '</m:oMath>'
    '</m:oMathPara>'
)

# Equation 5: Unsupported Claim Rate
xml5 = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:r><m:t>R_unsupported = </m:t></m:r>'
    '<m:f><m:num><m:r><m:t>N_contradicted + N_insufficient + N_conflicting</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_total)</m:t></m:r></m:den></m:f>'
    '</m:oMath>'
    '</m:oMathPara>'
)

# Equation 6: Risk score
xml6 = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:r><m:t>S_risk = min(1.0,  0.70 · R_contra + 0.30 · </m:t></m:r>'
    '<m:f><m:num><m:r><m:t>N_insufficient + N_conflicting</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_verifiable)</m:t></m:r></m:den></m:f>'
    '<m:r><m:t>)</m:t></m:r>'
    '</m:oMath>'
    '</m:oMathPara>'
)

for xml in [xml1, xml2, xml3, xml4, xml5, xml6]:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = docx.shared.Pt(4)
    p.paragraph_format.space_after = docx.shared.Pt(6)
    p._element.append(parse_xml(xml))

doc.save('test_math_builder.docx')
print('All 6 math equations built and parsed successfully!')
