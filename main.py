from ete3 import NCBITaxa, Tree
ncbi = NCBITaxa()

# ANSI escape code for blue color
BLUE = '\033[94m'
# ANSI escape code to reset color
RESET = '\033[0m'

class TreeNode:
    def __init__(
        self,
        node_name:str,
        tax_id:str,
        init_as_root_with_species:list[str]=None
    ):
        self.name = node_name
        self.taxid = tax_id
        self.children = {}

        # Prepare the data structures
        lineages = {}
        names = {}

        species_names=init_as_root_with_species

        if species_names is not None:
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
                self.insert_lineage(lineage, names)

    def add_child(self, child):
        if child.taxid not in self.children:
            self.children[child.taxid] = child
    
    def __repr__(self):
        return f"{self.name} ({self.taxid})"

    def insert_lineage(self, lineage, names):
        current_node = self
        for taxid in lineage[1:]:  # skip root as it's already created
            if taxid not in current_node.children:
                new_node = TreeNode(names[taxid], taxid)
                current_node.add_child(new_node)
            current_node = current_node.children[taxid]

    def print(self, depth=0):
        """
        print a simple representation of this tree

        the species names in the output are highlighted in color.
        """

        if len(self.children)==0:
            print(BLUE,end="")
        print("  " * depth + str(self))
        if len(self.children)==0:
            print(RESET,end="")

        for child in self.children.values():
            child.print(depth + 1)

    def print_compact_tree(self, depth=0, print_children=False):
        """
        Print a simplified version of the tree

        this shows only:
            - leafs
            - the most immediate common ancestor of any leaf or branch
            - i.e.: does NOT show intermediate branches

        the species names in the output are highlighted in color.
        """
        
        # Determine if the current node has leaf nodes as direct children
        has_species_as_direct_children = any(len(child.children) == 0 for child in self.children.values())
        
        # Construct the node label, highlighting species names in blue
        label = f"{self.name} ({self.taxid})"
        if len(self.children) == 0:  # This is a species node
            label = BLUE + label + RESET
        
        if print_children or has_species_as_direct_children:
            print("  " * depth + label)
        
        for child in self.children.values():
            # If the current node has species as direct children, print all children (species).
            # Otherwise, pass the flag down to print children only if they have species as direct children.
            child.print_compact_tree(depth + 1, print_children=has_species_as_direct_children or print_children)


    def build_ete_tree(self, parent=None)->Tree:
        """
        Recursively builds an ETE tree, attaching taxonomic information to each node.
        """
        # If this is the root node
        if parent is None:
            ete_node = Tree(name=self.name)
        else:
            ete_node = parent.add_child(name=self.name)

        # Attach a hypothetical taxonomic identifier to the node as an example of taxonomic information.
        # In a real scenario, this could be a NCBI Taxonomy ID or other relevant identifier.
        ete_node.add_features(taxid="TaxID_" + self.name.replace(" ", "_"))

        for child in self.children.values():
            child.build_ete_tree(parent=ete_node)

        return ete_node


species_names = [
    'Dendroctonus ponderosae', 'Anoplophora glabripennis', 'Leptinotarsa decemlineata', 
    'Onthophagus taurus', 'Agrilus planipennis', 'Nicrophorus vespilloides', 
    'Sitophilus oryzae', 'Diabrotica virgifera', 'Asbolus verrucosus', 'Photinus pyralis', 
    'Ignelater luminosus', 'Rhynchophorus ferrugineus', 'Tribolium madens', 
    'Zophobas morio', 'Tenebrio molitor', 'Cylas formicarius', 
    'Acanthoscelides obtectus', 'Callosobruchus analis', 'Callosobruchus maculatus', 'Callosobruchus chinensis'
]


root = TreeNode("root", 1, species_names)

# Print the tree
print("basic (custom) tree representation:")
root.print()
# print compact version of the tree
print("compact (custom) tree representation:")
root.print_compact_tree()


# construct ete3 tree from custom data structure
ete_tree = root.build_ete_tree()

# print ete3 tree
print("basic newick tree:")
print(ete_tree.write(format=1))

# For visualization, print the tree showing taxid annotations
# this is a quite useful representation, with more information than the default newick tree 
print("well-formatted ASCII ete3 tree:")
print(ete_tree.get_ascii(show_internal=True, attributes=["name", "taxid"]))

# save the tree as newick tree to a file, and include the taxid feature in each leaf
ete_tree.write(outfile="tree_with_taxid.newick",features=["taxid", "path_score"])
