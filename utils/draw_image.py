
from app.models import *
import networkx as nx
from matplotlib import pylab as plt


def draw_gragh(node_wlibnames, file_name):
    """

    :param node_models:
    :return:
    """
    g = nx.DiGraph()
    g.add_nodes_from(node_wlibnames)
    edge_list_s = []
    edge_list_d = []
    res = []
    user = User.objects.get(id=1)
    # ==================  for each wlibnames , check relation ============================
    for ind_1, t1 in enumerate(node_wlibnames):
        for ind_2, t2 in enumerate(node_wlibnames[ind_1 + 1:]):
            r = Relation.objects.filter(t1__name=t1, t2__name=t2).values('l_name_r__r_name', 'id')
            if r:
                # relation exists
                if str(r[0]['l_name_r__r_name']) == '<=':
                    edge_list_s.append((t1, t2))
                    res.append((t1, t2, r[0]['l_name_r__r_name'], r[0]['id']))
            else:
                # relation not exists
                obj_1 = Wlibrary.objects.get(name=t1)
                obj_2 = Wlibrary.objects.get(name=t2)
                if obj_1.mcdc_1 > obj_2.mcdc_2:
                    # check mcdc
                    try:
                        nexus = Nexus.objects.get(r_name='<=')
                    except:
                        nexus = Nexus.objects.create(r_name='<=')
                    r = Relation.objects.create(t1=obj_2, t2=obj_1, l_name_r=nexus,
                                                user=user, l_name_exp='', ref='')
                    edge_list_s.append((t2, t1))
                    res.append((t2, t1, "<=", r.id))
                elif obj_1.mcdc_2 < obj_2.mcdc_1:
                    try:
                        nexus = Nexus.objects.get(r_name='<=')
                    except:
                        nexus = Nexus.objects.create(r_name='<=')
                    r = Relation.objects.create(t1=obj_1, t2=obj_2, l_name_r=nexus,
                                                user=user, l_name_exp='', ref='')
                    edge_list_s.append((t1, t2))
                    res.append((t1, t2, "<=", r.id))
                # default
                else:
                    edge_list_d.append((t1, t2))

    # ==========  draw image   ===================

    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_size=700, label=True)
    nx.draw_networkx_edges(g, pos, edgelist=edge_list_s, edge_color='k', style='solid',
                           width=3, label=True)
    nx.draw_networkx_edges(g, pos, edgelist=edge_list_d, width=3, edge_color='b', style='dashed')
    nx.draw_networkx_labels(g, pos)
    nx.draw_networkx_edge_labels(g, pos)
    plt.axis('off')
    plt.savefig(file_name + ".png")  # save as png
    plt.close()
    return res
