from collections.__init__ import OrderedDict

DBPEDIA_ENDPOINT = "http://dbpedia.org/sparql/"

DBPEDIA_REPLACE_RULES = OrderedDict()

DBPEDIA_REPLACE_RULES["brack_open"] = '{' # \n
DBPEDIA_REPLACE_RULES["brack_close"] = '}'
# DBPEDIA_REPLACE_RULES["attr_open"] = '('
# DBPEDIA_REPLACE_RULES[' \( '] = '('
# DBPEDIA_REPLACE_RULES["attr_close"] = ')'
# DBPEDIA_REPLACE_RULES[' \) '] = ')'
DBPEDIA_REPLACE_RULES["var_"] = '?'
DBPEDIA_REPLACE_RULES["sep_dot"] = '.' # \n
DBPEDIA_REPLACE_RULES["_oba_"] = 'order by asc'
DBPEDIA_REPLACE_RULES["_obd_"] = 'order by desc'
DBPEDIA_REPLACE_RULES["dbr_"] = 'dbr:'
DBPEDIA_REPLACE_RULES["dbo_"] = 'dbo:'
DBPEDIA_REPLACE_RULES["rdfs_"] = 'rdfs:'
DBPEDIA_REPLACE_RULES["rdf_"] = 'rdf:'
DBPEDIA_REPLACE_RULES["foaf_"] = 'foaf:'
DBPEDIA_REPLACE_RULES["dbp_"] = 'dbp:'
DBPEDIA_REPLACE_RULES["math_gt"] = ' > '
DBPEDIA_REPLACE_RULES["math_lt"] = ' < '

DBPEDIA_REGEX_REPLACE_RULES = OrderedDict()
DBPEDIA_REGEX_REPLACE_RULES[r"\s{2,}"] = " "
DBPEDIA_REGEX_REPLACE_RULES[r"\s(\s"] = " attr_open "
DBPEDIA_REGEX_REPLACE_RULES[r"\s)\s"] = " attr_close "

DBPEDIA_REGEX_BACK_REPLACE_RULES = OrderedDict()

DBPEDIA_REGEX_BACK_REPLACE_RULES["\s{2,}"] = " "
DBPEDIA_REGEX_BACK_REPLACE_RULES[r"dbr_(\S+?)_ attr_open (.+?) attr_close"] = "dbr_\g<1>_(\g<2>)"
DBPEDIA_REGEX_BACK_REPLACE_RULES[r"dbr_ attr_open (.+?) attr_close _(\S+?)"] = "dbr_(\g<1>)_\g<2>"
DBPEDIA_REGEX_BACK_REPLACE_RULES[r",'"] = " , '"
DBPEDIA_REGEX_BACK_REPLACE_RULES[r"attr_open"] = " ( "
DBPEDIA_REGEX_BACK_REPLACE_RULES[r"attr_close"] = " ) "
DBPEDIA_REGEX_BACK_REPLACE_RULES["\s{2,}"] = " "


DBPEDIA_PREFIXES = {
    "dbr": "http://dbpedia.org/resource/",
    "res": "http://dbpedia.org/resource/",
    "dbp": "http://dbpedia.org/property/",
    "dbo": "http://dbpedia.org/ontology/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}
