

from semantic_network import *
from bayes_net import *


class MySN(SemanticNetwork):

    def query_dependents(self, entity):
        """
        Works by filtering all the relations in the network that are Subtypes or Depends on entity E.
        Then if that relation is of Dependency, we check if that entity(1) is a Supertype: if so, we add the children
        else itself.
        We continue to iterate through the relations, to further explore the network

        :param entity: Entity E of the network
        :return: returns the list of all entities whose operation depends on the correct operation of E
        """
        relations = set([d.relation for d in self.declarations
                          if d.relation.entity2 == entity and (
                                      isinstance(d.relation, Subtype) or isinstance(d.relation, Depends))])

        temp_list = []
        for rel in relations:
            if isinstance(rel, Depends):
                subtypes_list = [d.relation.entity1 for d in self.query_local(e2=rel.entity1, rel="subtype")]
                temp_list += subtypes_list if subtypes_list else [rel.entity1]

            temp_list += self.query_dependents(rel.entity1)

        return list(set(temp_list))


    def query_causes(self, entity):
        """
        Works by filtering all the relations in the network that are Subtypes or Depends on entity E.
        Then if that relation is of Dependency, we add that entity(1) itself.
        We continue to iterate through the relations, to further explore the network

        :param entity: Entity E of the network
        :return: the list of all entities whose failure or malfunction can cause failure or malfunction in E
        """
        relations = [d.relation for d in self.declarations if (isinstance(d.relation, Depends) \
                or isinstance(d.relation, Subtype))and d.relation.entity1 == entity]

        # new_list = []
        # for rel in relations:
        #     if isinstance(rel, Depends):
        #         print("[ADDING]: ", rel.entity2)
        #         new_list.append(rel.entity2)
        #     new_list += (self.query_causes(rel.entity2))

        # https://stackoverflow.com/a/3766765
        new_list = [result for rel in relations for result in (self.query_causes(rel.entity2)) + ([rel.entity2] if isinstance(rel, Depends) else []) ]

        return list(set(new_list))

    def query_causes_sorted(self,entity):
        """
        Internally, aggregates all the T time values of a E Entity in a dictionary as dict[E] = [T1,T2,...];
        So that it by last calculates the mean of these values for each E

        :param entity: Entity E of the network
        :return: list of tuples (X, T), where X is an entity whose failure or malfunction can cause damage or
        malfunction of E (X is a potential cause of the problem observed in E) and T is the average time required
        to analyze X.
        """
        # new_dict = {}
        # for i in causes:
        #     temp_list = []
        #     for decl in self.query_local(rel="debug_time", e1=i):
        #         temp_list.append(decl.relation.entity2)
        #     new_dict[i] = temp_list

        temp_dict = { c_entity : [decl.relation.entity2 for decl in self.query_local(rel="debug_time", e1=c_entity)] for c_entity in self.query_causes(entity)  }
        return sorted([(key, sum(temp_dict[key]) / len(temp_dict[key])) for key in temp_dict], key=lambda item: (item[1], item[0]))


class MyBN(BayesNet):

    def markov_blanket(self,var):
        """
        Internally, gathers all the children of var. Then lists all the parents of var+children, excluding
        of course, var.
        Finally returns children + parents

        :param var: variable of the network
        :return: list of the variables that make up the Markov blanket of that variable.
        """
        # filhos = []
        #
        # for entity in list(self.dependencies):
        #     for p in list(self.dependencies[entity])[0]:
        #         if p[0] == var:
        #             print("UAU")
        #             filhos.append(entity)

        children_list = [entity for entity in list(self.dependencies) for mother in list(self.dependencies[entity])[0] if mother[0] == var]
        # print("[CHILDREN_LIST]: ", children_list)

        # parent_list = []
        # print(children_list + [var])
        # for entity in children_list + [var]:
        #     print("[SEPARATOR]", entity, list(self.dependencies[entity])[0])
        #     for mother in list(self.dependencies[entity])[0]:
        #         print("-->> ", list(mother))
        #         for p in list(mother):
        #             print("p1 -->> :", p)
        #         if mother[0] != var:
        #             print("[APPENDING] ", mother[0])
        #             parent_list.append(mother[0])
        #
        # print("[PARENT_LIST]: ", parent_list)

        final_list = [mother[0] for entity in (children_list + [var]) for mother in list(self.dependencies[entity])[0] if mother[0] != var] + children_list

        # Note: it seems like it has no necessity of converting to set(), but as it had little testing, it is used just in case
        return list(set(final_list))





