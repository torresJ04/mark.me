"""Mark.me — destaque termos em PDF com cor personalizada (GUI e CLI)."""
from mark_me.core import (
    contar_ocorrencias,
    contar_ocorrencias_multi,
    destacar_pdf,
    destacar_pdf_multi,
    hex_to_rgb_normalized,
)

__all__ = [
    "contar_ocorrencias",
    "contar_ocorrencias_multi",
    "destacar_pdf",
    "destacar_pdf_multi",
    "hex_to_rgb_normalized",
]
