from collections.__init__ import OrderedDict

WIKIDATA_ENDPOINT_URL = "https://query.wikidata.org/sparql"
MY_ENDPOINT_URL = "https://qa.imfd.cl/sparql"

WIKIDATA_REPLACE_RULES = OrderedDict()
WIKIDATA_REPLACE_RULES["brack_open"] = '{'  # \n
WIKIDATA_REPLACE_RULES["brack_close"] = '}'
WIKIDATA_REPLACE_RULES["attr_open"] = '('
# WIKIDATA_REPLACE_RULES[' \( '] = '('
WIKIDATA_REPLACE_RULES["attr_close"] = ')'
# WIKIDATA_REPLACE_RULES[' \) '] = ')'
WIKIDATA_REPLACE_RULES["var_"] = '?'
WIKIDATA_REPLACE_RULES["sep_dot"] = '.'  # \n
WIKIDATA_REPLACE_RULES["sep_comma"] = ','  # \n
WIKIDATA_REPLACE_RULES["_oba_"] = 'order by asc'
WIKIDATA_REPLACE_RULES["_obd_"] = 'order by desc'
WIKIDATA_REPLACE_RULES["_grb_"] = 'group by'
WIKIDATA_REPLACE_RULES["wd_"] = 'wd:'
WIKIDATA_REPLACE_RULES["wdt_"] = 'wdt:'
WIKIDATA_REPLACE_RULES["rdfs_"] = 'rdfs:'
WIKIDATA_REPLACE_RULES["rdf_"] = 'rdf:'
WIKIDATA_REPLACE_RULES["foaf_"] = 'foaf:'
WIKIDATA_REPLACE_RULES["p_"] = 'p:'
WIKIDATA_REPLACE_RULES["ps_"] = 'ps:'
WIKIDATA_REPLACE_RULES["pq_"] = 'pq:'
WIKIDATA_REPLACE_RULES["bd_"] = 'bd:'

WIKIDATA_REGEX_REPLACE_RULES = OrderedDict()
WIKIDATA_REGEX_REPLACE_RULES[r"<([\w\d_]+)>"] = r'placeholder_\1'
WIKIDATA_REGEX_REPLACE_RULES[r"(\d)[.](\d)"] = r"\1_dot_\2"
WIKIDATA_REGEX_REPLACE_RULES[r"'(.*?)'"] = r"apstrph_\1_apstrph"
WIKIDATA_REGEX_REPLACE_RULES[r"\s*([}{)(.,><=])\s*"] = r" \1 "
WIKIDATA_REGEX_REPLACE_RULES[">"] = 'math_gt'
WIKIDATA_REGEX_REPLACE_RULES["<"] = 'math_lt'
WIKIDATA_REGEX_REPLACE_RULES["="] = 'math_eq'
WIKIDATA_REGEX_REPLACE_RULES[r"\s{2,}"] = ' '
#WIKIDATA_REGEX_REPLACE_RULES[r'([,])\s*\"'] = r'\1 open_quote'
#WIKIDATA_REGEX_REPLACE_RULES[r'\"\s*([)])'] = r'\1 close_quote'

WIKIDATA_REGEX_BACK_REPLACE_RULES = OrderedDict()
WIKIDATA_REGEX_BACK_REPLACE_RULES[r"placeholder_(\w+)"] = r'<\1>'
WIKIDATA_REGEX_BACK_REPLACE_RULES[r"(\d)_dot_(\d)"] = r"\1.\2"
WIKIDATA_REGEX_BACK_REPLACE_RULES[r"apstrph_(.*?)_apstrph"] = r"'\1'"
WIKIDATA_REGEX_BACK_REPLACE_RULES["math_gt"] = ' > '
WIKIDATA_REGEX_BACK_REPLACE_RULES["math_lt"] = ' < '
WIKIDATA_REGEX_BACK_REPLACE_RULES["math_eq"] = ' = '
#WIKIDATA_REGEX_BACK_REPLACE_RULES['open_quote'] = '\"'
#WIKIDATA_REGEX_BACK_REPLACE_RULES['close_quote'] = '\"'

WIKIDATA_PREFIXES = OrderedDict()
WIKIDATA_PREFIXES["wd"] = "http://www.wikidata.org/entity/"
WIKIDATA_PREFIXES["wdt"] = "http://www.wikidata.org/prop/direct/"
WIKIDATA_PREFIXES["wiki"] = "https://en.wikipedia.org/wiki/"
WIKIDATA_PREFIXES["wikibase"] = "http://wikiba.se/ontology#"
WIKIDATA_PREFIXES["ps"] = "http://www.wikidata.org/prop/statement/"
WIKIDATA_PREFIXES["pq"] = "http://www.wikidata.org/prop/qualifier/"
WIKIDATA_PREFIXES["p"] = "http://www.wikidata.org/prop/"
WIKIDATA_PREFIXES["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
WIKIDATA_PREFIXES["bd"] = "http://www.bigdata.com/rdf#"
WIKIDATA_PREFIXES["schema"] = "http://schema.org/"
WIKIDATA_PREFIXES["skos"] = "http://www.w3.org/2004/02/skos/core#"
