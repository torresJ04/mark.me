"""
Mark.me - Lógica de destaque em PDF (compartilhada por GUI e CLI).
"""
import fitz  # PyMuPDF


def hex_to_rgb_normalized(hex_color: str) -> tuple[float, float, float]:
    """Converte cor hexadecimal (#RRGGBB) para RGB normalizado (0-1) para PyMuPDF."""
    hex_color = (hex_color or "").strip().lstrip("#")
    if len(hex_color) != 6:
        return (1.0, 1.0, 0.0)
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)


def contar_ocorrencias(input_path: str, termo_busca: str) -> int:
    """Retorna o número de ocorrências do termo no PDF (verificação rápida, sem gravar)."""
    doc = fitz.open(input_path)
    total = 0
    for pagina in doc:
        total += len(pagina.search_for(termo_busca))
    doc.close()
    return total


def contar_ocorrencias_multi(input_path: str, termos: list[str]) -> int:
    """Retorna o total de ocorrências de todos os termos no PDF."""
    doc = fitz.open(input_path)
    total = 0
    for pagina in doc:
        for termo in termos:
            total += len(pagina.search_for(termo))
    doc.close()
    return total


def destacar_pdf(input_path: str, output_path: str, termo_busca: str, hex_color: str) -> None:
    """Aplica marca-texto no PDF com o termo e cor indicados."""
    destacar_pdf_multi(input_path, output_path, [(termo_busca, hex_color)])


def destacar_pdf_multi(
    input_path: str,
    output_path: str,
    pares: list[tuple[str, str]],
) -> None:
    """Aplica marca-texto no PDF para vários (termo, cor_hex). Cada termo com sua cor."""
    pares = [(t.strip(), c) for t, c in pares if t and t.strip()]
    if not pares:
        raise ValueError("Nenhum termo informado.")
    doc = fitz.open(input_path)
    for pagina in doc:
        for termo_busca, hex_color in pares:
            rgb = hex_to_rgb_normalized(hex_color)
            instancias = pagina.search_for(termo_busca)
            for inst in instancias:
                annot = pagina.add_highlight_annot(inst)
                annot.set_colors(stroke=rgb)
                annot.update()
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
