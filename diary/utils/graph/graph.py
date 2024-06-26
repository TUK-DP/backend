import os
from datetime import datetime

import numpy as np
from dotenv import load_dotenv
from neo4j import GraphDatabase

# load .env
load_dotenv()

NEO4J_PASSWORD = os.environ.get('NEO4j_PASSWORD')


class GraphDB:
    """GraphDP 모듈입니다.

    GraphDB는 Neo4j 데이터베이스에 접근하여 키워드 노드를 추가하고, 노드들을 연결합니다.

    usage:
        conn = GraphDB()
        conn.create_and_link_nodes(...)
        conn.find_all_by_user_diary(...)
    """

    def __init__(self):
        self._driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", NEO4J_PASSWORD))
        print("GraphDB connected")

    def close(self):
        self._driver.close()

    def delete_diary(self, user_id: int, diary_id: int):
        """user_id와 diary_id에 해당하는 일기와 연결된 노드들을 삭제합니다.

        :param user_id: 유저의 ID.
        :param diary_id: 일기의 ID.
        """

        with self._driver.session() as session:
            session.execute_write(
                self._delete_diary,
                user_id=user_id,
                diary_id=diary_id
            )

    def create_and_link_nodes(
            self, user_id: int, diary_id: int,
            words_graph: np.ndarray = None,
            words_dict: dict = None,
            weights_dict: dict = None
    ):
        """그래프 데이터베이스에 키워드 노드를 추가합니다.

        그래프 데이터베이스에 키워드 노드를 추가하고, 노드들을 연결합니다.
        이전에 userId, diaryId에 해당하는 노드가 존재한다면 초기화 이후 새로운 노드를 추가합니다.

        :param user_id: 유저의 ID.

        :param diary_id: 일기의 ID.

        :param diary_date: 일기의 날짜. datetime 객체.

        :param words_graph: 이차원 Numpy 배열. 각 원소는 키워드의 tfidf 이며 TextRank.words_graph 와 같다.

        :param words_dict: 단어의 dictionary. {word_index: word_text} == TextRank.words_dict

        :param weights_dict: 단어들의 가중치 dictionary. {index: weight} == Rank.get_ranks(graph)

        usage:
                db.insert_node(
                    userId,diaryId, diary_date,
                    words_graph=TextRank.words_graph,
                    words_dict=TextRank.words_dict,
                    weights_dict=Rank.get_ranks(graph)
                )
        """

        with self._driver.session() as session:
            # Delete previous keyword nodes and relationships
            session.execute_write(
                self._delete_diary,
                user_id=user_id,
                diary_id=diary_id
            )

            # Create and link nodes
            session.execute_write(
                self._create_and_link_nodes,
                user_id, diary_id,
                words_graph, words_dict, weights_dict
            )

    def find_all_by_user_diary(self, user_id: int, diary_id: int):
        """user 와 diary 에 연결된 모든 노드를 찾는다.

        :param user_id: 유저의 ID.
        :param diary_id: 일기의 ID.

        :return: {
            User : {
                user_id
            },
            Diary : {
                diary_id,
                date,
            }
            CONNECTED : [
                {
                    tfidf : tfidf,
                    start : {
                        text,
                        weight
                    },
                    end : {
                        text,
                        weight
                    }
                },
                ...
            ],
        }
        """

        with self._driver.session() as session:
            return session.execute_write(self._find_all_by_user_diary, user_id, diary_id)

    @staticmethod
    def _find_all_by_user_diary(tx, user_id: int, diary_id: int):
        dic = {"User": {}, "Diary": {}, "nodes": [], "relationships": []}

        # Find User and Diary nodes
        user_diary = tx.run(
            f"MATCH (u:User {{ user_id: {user_id} }})-[:WROTE]-(d:Diary {{diary_id: {diary_id}}})"
            "RETURN u, d"
        )

        for n in user_diary:
            dic['User'] = {
                "id": n['u'].id,
                "user_id": n['u']['user_id'],
                "label": "User",
                "text": "나"
            }

            dic['Diary'] = {
                "id": n['d'].id,
                "diary_id": n['d']['diary_id'],
                "label": "Diary",
                "text": "일기"
            }

            dic['nodes'].append(dic['User'])
            dic['nodes'].append(dic['Diary'])
            dic['relationships'].append({
                "properties": {},
                "type": "WROTE",
                'startNode': dic['User']['id'],
                'endNode': dic['Diary']['id']
            })

        # Find Keywords include in Diary
        include_result = tx.run(f"MATCH (d:Diary {{diary_id : {diary_id}}})-[:INCLUDE]-(k:Keyword) RETURN k, d")
        for n in include_result:
            k_node = n['k']

            dic['nodes'].append({
                "id": k_node.id,
                "label": "Keyword",
                "text": k_node['text'],
                'weight': k_node['weight']
            })

            d_node = n['d']

            dic['relationships'].append({
                "properties": {},
                "type": "INCLUDE",
                'startNode': d_node.id,
                'endNode': k_node.id
            })

        # Find connected Keywords and include in Diary
        connected_result = tx.run(
            f"MATCH (:Diary {{diary_id : {diary_id}}})-[:INCLUDE]-(k:Keyword) "
            "MATCH (k)-[c:CONNECTED]-(other:Keyword) "
            "RETURN k, other, c"
        )

        for record in connected_result:
            a_node = record['k']
            b_node = record['other']
            connect = record['c']

            dic['relationships'].append({
                "properties": {
                    'tfidf': connect['tfidf']
                },
                "type": "CONNECTED",
                'startNode': a_node.id,
                'endNode': b_node.id
            })

        return dic

    @staticmethod
    def _create_and_link_nodes(
            tx,
            user_id, diary_id,
            words_graph: np.ndarray = None, words_dict: dict = None, weights_dict: dict = None
    ):

        # Create relationship between User and Diary
        tx.run(
            "MERGE (u:User {user_id: $user_id}) "
            "MERGE (d:Diary {diary_id: $diary_id}) "
            "MERGE (u)-[:WROTE]->(d) "
            , user_id=user_id, diary_id=diary_id
        )

        # words_graph[i][j] = weight of word i => word i
        # Create Keyword nodes and their relationships
        for i, row in enumerate(words_graph):
            # row[j] = weight of word i => word j
            for j, weight in enumerate(row):
                if i == j:
                    continue
                if weight == 0:
                    continue

                # Create Keyword nodes
                tx.run(
                    "MERGE (d:Diary {diary_id: $diary_id}) "
                    "MERGE (d)-[:INCLUDE]-(k1:Keyword {text: $text1, weight: $weight1}) "
                    "MERGE (d)-[:INCLUDE]-(k2:Keyword {text: $text2, weight: $weight2}) "
                    "MERGE (k1)-[:CONNECTED {tfidf: $tfidf}]->(k2) ",
                    diary_id=diary_id,
                    text1=words_dict[i],
                    text2=words_dict[j],
                    weight1=weights_dict[i],
                    weight2=weights_dict[j],
                    tfidf=words_graph[i][j]
                )

    @staticmethod
    def _delete_diary(
            tx,
            user_id, diary_id
    ):
        # Delete previous keyword nodes and relationships
        tx.run(
            "MATCH (u:User {user_id: $user_id})-[w:WROTE]-(d:Diary {diary_id: $diary_id}) "
            "DELETE w "
            "WITH d "
            "MATCH (d)-[i:INCLUDE]-(k:Keyword)-[c:CONNECTED]-(k2:Keyword)-[:INCLUDE]-(d) "
            "DELETE i,c,k,k2 "
            , user_id=user_id, diary_id=diary_id
        )

        # Delete Diary node
        tx.run(
            "MATCH (d:Diary {diary_id: $diary_id}) "
            "DELETE d"
            , diary_id=diary_id
        )
