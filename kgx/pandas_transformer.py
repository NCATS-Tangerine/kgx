import pandas as pd
import logging
from .transformer import Transformer

class PandasTransformer(Transformer):
    """
    Implements Transformation from a Pandas DataFrame to a NetworkX graph
    """
    
    def parse(self, filename, **args):
        """
        Parse a CSV/TSV

        May be either a node file or an edge file
        """
        df = pd.read_csv(filename, comment='#', **args)
        self.load(df)
        
    def load(self, df):
        if 'subject' in df:
            self.load_edges(df)
        else:
            self.load_nodes(df)
            
    def load_nodes(self, df):
        for obj in df.to_dict('record'):
            self.load_node(obj)
            
    def load_node(self, obj):
        id = obj['id']
        self.graph.add_node(id, attr_dict=obj)
            
    def load_edges(self, df):
        for obj in df.to_dict('record'):
            self.load_edge(obj)

    def load_edge(self, obj):
        s = obj['subject']
        o = obj['object']
        self.graph.add_edge(o, s, attr_dict=obj)

    def export_nodes(self):
        items = []
        for n,data in self.graph.nodes_iter(data=True):
            item = data.copy()
            item['id'] = n
            items.append(item)
        df = pd.DataFrame.from_dict(items)
        return df
    
    def export_edges(self):
        items = []
        for o,s,data in self.graph.edges_iter(data=True):
            item = data.copy()
            item['subject'] = s
            item['object'] = o
            items.append(item)
        df = pd.DataFrame.from_dict(items)
        cols = df.columns.tolist()
        cols = self.order_cols(cols)
        df = df[cols]
        return df

    def order_cols(self, cols):
        ORDER = ['id', 'subject', 'predicate', 'object', 'relation']
        cols2 = []
        for c in ORDER:
            if c in cols:
                cols2.append(c)
                cols.remove(c)
        return cols2 + cols
        
        
    def save(self, filename, type='n', **args):
        """
        Write a CSV/TSV

        May be either a node file or an edge file
        """
        if type == 'n':
            df = self.export_nodes()
        else:
            df = self.export_edges()
        # TODO: order
        df.to_csv(filename, index=False)