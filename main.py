from ete3 import NCBITaxa
ncbi = NCBITaxa()

class TreeNode:
    def __init__(self, name, taxid):
        self.name = name
        self.taxid = taxid
        self.children = {}

    def add_child(self, child):
        if child.taxid not in self.children:
            self.children[child.taxid] = child
    
    def __repr__(self):
        return f"{self.name} ({self.taxid})"

def insert_lineage(root, lineage, names):
    current_node = root
    for taxid in lineage[1:]:  # skip root as it's already created
        if taxid not in current_node.children:
            new_node = TreeNode(names[taxid], taxid)
            current_node.add_child(new_node)
        current_node = current_node.children[taxid]

def print_tree(node, depth=0):
    print("  " * depth + str(node))
    for child in node.children.values():
        print_tree(child, depth + 1)

species_names = [
    'Dendroctonus ponderosae', 'Anoplophora glabripennis', 'Leptinotarsa decemlineata', 
    'Onthophagus taurus', 'Agrilus planipennis', 'Nicrophorus vespilloides', 
    'Sitophilus oryzae', 'Diabrotica virgifera', 'Asbolus verrucosus', 'Photinus pyralis', 
    'Ignelater luminosus', 'Rhynchophorus ferrugineus', 'Tribolium madens', 
    'Zophobas morio', 'Tenebrio molitor', 'Cylas formicarius', 
    'Acanthoscelides obtectus', 'Callosobruchus analis', 'Callosobruchus maculatus', 'Callosobruchus chinensis'
]

# Prepare the data structures
lineages = {}
names = {}
root = TreeNode("root", 1)

# Query NCBI and fill `lineages` and `names`
for species in species_names:
    taxid = ncbi.get_name_translator([species]).get(species, [None])[0]
    if taxid:
        lineage_ids = ncbi.get_lineage(taxid)
        lineage_names = ncbi.get_taxid_translator(lineage_ids)
        lineages[species] = lineage_ids
        names.update(lineage_names)

# Insert lineages into the tree
for species, lineage in lineages.items():
    insert_lineage(root, lineage, names)

# Print the tree
print_tree(root)
