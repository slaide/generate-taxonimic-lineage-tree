from ete3 import NCBITaxa

ncbi = NCBITaxa()

class TreeNode:
    def init(self, name, taxid):
        self.name = name
        self.taxid = taxid
        self.children = {}
    
    def add_child(self, child):
        if child.taxid not in self.children:
            self.children[child.taxid] = child
    
    def repr(self):
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

species_names = ['Dendroctonus ponderosae', 'Anoplophora glabripennis', 'Leptinotarsa decemlineata', 
                 'Onthophagus taurus', 'Agrilus planipennis', 'Nicrophorus vespilloides', 
                 'Sitophilus oryzae', 'Diabrotica virgifera', 'Asbolus verrucosus', 'Photinus pyralis',
                 'Ignelater luminosus', 'Rhynchophorus ferrugineus', 'Tribolium madens', 
                 'Dendroctonus ponderosae', 'Zophobas morio', 'Tenebrio molitor', 
                 'Cylas formicarius', 'Acanthoscelides obtectus', 'Callosobruchus analis', 
                 'Callosobruchus maculatus', 'Callosobruchus chinensis']

# Assuming 'lineages' is a dict with species names as keys and their lineage (list of taxids) as values
# 'names' is a dict with taxid as keys and taxonomic names as values
lineages = {}
names = {}

root = TreeNode("root", 1)

for species, lineage in lineages.items():
    insert_lineage(root, lineage, names)

# Query NCBI and fill lineages and names
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
