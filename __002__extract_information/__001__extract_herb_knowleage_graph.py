from __002__extract_information.__000__extract_graph_data_utils import extract_formula_graph
from common.path_utils import get_file_path

extract_formula_graph(get_file_path("__001__clawler/中药"),
                      output_path=get_file_path("__002__extract_information/herb_graph.json"),
                      resume=True)