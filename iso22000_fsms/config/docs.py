"""Configuration for docs page generation (frappe build_docs)."""

source_link = "https://github.com/mrhuychien/iso22000_fsms"
docs_base_url = "/docs"
headline = "ISO 22000 FSMS"
sub_heading = "Hệ thống quản lý ATTP theo ISO 22000:2018"


def get_context(context):
	context.brand_html = "ISO 22000 FSMS"
