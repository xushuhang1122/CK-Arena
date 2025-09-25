





class player_prompt_en:

    
    def system_speak_player():
        p = f"""
            
            You are an AI player participating in the "Who is the Undercover" game. You need to analyze the situation based on the information received, determine your identity, and devise appropriate speaking strategies and content.

            # Game Rules

            1. Each player receives a word. The majority of players receive the same word (civilians), while a minority (1-2 players) receive a different but related word (undercover agents).
            2. The game proceeds in turns, with each player using one sentence to describe their word without directly saying it.
            3. After each round of descriptions, all players vote for who they think is the undercover agent. The player with the most votes is eliminated.
            4. If all undercover agents are eliminated, the civilians win; if the number of undercover agents equals or exceeds the number of civilians, the undercover agents win.

            # Speaking Requirements

            1. Your statement must be a brief descriptive sentence, not a lengthy exposition.
            2. You cannot repeat statements made by other players in previous rounds.
            3. Your description can be broad or specific, but must match the word you received. You cannot give descriptions that do not match your word.
            4. Please adjust the level of detail in your description according to your strategic needs. Below are examples of different levels of detail.

            # Description Examples
            (Assuming the word to describe is "soccer ball")
            "A spherical object" - Detail level 0.2 (too broad, many objects are spherical)
            "A sports equipment" - Detail level 0.4 (more specific, but still covers a wide range)
            "Mostly contacted by the lower body of athletes" - Detail level 0.6 (more specific, stronger directional indication)
            "Commonly depicted with a pattern of black and white pentagons and hexagons" - Detail level 0.8 (very specific, almost only soccer balls look like this)
            "One of the most popular sports in the world, seen being kicked and headed by athletes on a green field" - Detail level 1.0 (completely points to soccer ball)



            # Your Task

            1. Based on the given word and other players' statements, analyze your possible identity (civilian or undercover agent)
            2. With the goal of protecting yourself and accomplishing your game objective, provide your statement content.
            3. Provide your analysis and decision-making process in JSON format

            # Output Requirements

            You must respond in JSON format, including the following fields:
            {{
            "identity": "Analysis of your own and other players' identities",
            "strategy": "Your thinking and decision-making process",
            "statement": "Your final statement (you cannot include your analysis process in the statement field, and you cannot directly mention your word)"
            }}

            # Strategy Tips

            ### At the beginning of the game or when identity is still undetermined: 
            
            start with very vague, broad characteristics or properties, then provide more detailed descriptions of the word after gradually determining your identity situation.

            ### As a civilian (you need to determine your civilian identity yourself):

            Analyze other players' statements to find descriptions inconsistent with the majority
            Gradually narrow down the word range to help identify the undercover agent
            Ensure your description matches your word, don't say anything inconsistent with it


            ### As an undercover agent (you need to determine your undercover identity yourself):

            Carefully analyze civilian statements to infer their word
            Use vague descriptions that won't immediately arouse suspicion
            Ensure your description can match both your word and the civilians' word (ambiguity)
            Avoid descriptions obviously different from others, but don't completely follow them
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Here is information related to this game round. Please analyze this information to complete your task.
            # Your personal information:
            You are player_{player_id}, your word is "{assigned_concept}".
            # Statement history for this game round:
            {statement_history}
            # Your identity analysis from the previous round:
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        You are an AI player participating in the "Who is the Undercover" game. You need to analyze the situation based on the information received, determine your identity, and decide to vote for a player to try to eliminate them.

        # Game Rules

        1. Each player receives a word. The majority of players receive the same word (civilians), while a minority (1-2 players) receive a different but related word (undercover agents).
        2. The game proceeds in turns, with each player using one sentence to describe their word without directly saying it.
        3. After each round of descriptions, all players vote for who they think is the undercover agent. The player with the most votes is eliminated.
        4. If all undercover agents are eliminated, the civilians win; if the number of undercover agents equals or exceeds the number of civilians, the undercover agents win.

        # Your Task

        1. Based on the given word and other players' statements, analyze your possible identity (civilian or undercover agent)
        2. With the goal of protecting yourself and accomplishing your game objective, provide your statement content.
        3. Provide your analysis and decision-making process in JSON format

        # Output Requirements

        You must respond in JSON format, including the following fields:
        {{
        "identity": "Analysis of your identity",
        "strategy": "Thinking about your strategy",
        "vote": "The player you want to vote for (just a number, no additional text explanation needed)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Here is information related to this game round. Please analyze this information to complete your task.
            # Your personal information:
            You are player_{player_id}, your word is "{assigned_concept}".
            # The description history for this game round is:
            {statement_history}
            # Your identity analysis from the previous round:
            {last_analyze}
            # The list of currently surviving players is:
            {alive_players}
            You can only choose one number from these as your vote.
        """
        return p 












class judge_prompt_en:


    def system_judge():
        p = f"""
            
            # Who is the Undercover Game Referee Guide

            You are the referee for the "Who is the Undercover" game, responsible for analyzing each player's statement and scoring it according to the following criteria. You need to output your evaluation results in JSON format.

            ## Evaluation Dimensions

            1. **Novelty**：Whether the current statement repeats content from previous players' statements
            - 0: Completely repeats a previous player's description
            - 0.2: Mostly repetitive, with only minimal new information
            - 0.4: Partially repeats previous content, with some additional content
            - 0.6: Mainly new content, but with some repetition
            - 0.8: Almost entirely new content, with a different perspective from previous descriptions
            - 1.0: Completely novel description, providing an entirely new perspective or information

            2. **Relevance**：The degree of relevance and specificity between the statement and the word's characteristics
            - 0: Completely irrelevant
            - 0.2: Extremely broad description, applicable to a large number of objects/concepts
            - 0.4: Broad but somewhat directional description
            - 0.6: Clear clues, but could still point to multiple similar things
            - 0.8: Highly specific description, basically only pointing to the target word or very few similar objects
            - 1.0: Description that almost directly points to the word

            3. **Reasonableness**：How reasonable the association between the description and the word is
            - 0: Completely unreasonable, impossible to establish any association with the word
            - 0.2: Extremely far-fetched association
            - 0.4: Some association but rather far-fetched
            - 0.6: Reasonable but not unique association
            - 0.8: Highly reasonable association
            - 1.0: Description completely matching the word's characteristics

            ## Output Format

            ```json
            {{
                "novelty": {{
                "score": Value between 0 and 1 (limited to 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explanation for why this score was given"
                }},
                "relevance": {{
                "score": Value between 0 and 1 (limited to 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explanation for why this score was given"
                }},
                "reasonableness": {{
                "score": Value between 0 and 1 (limited to 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explanation for why this score was given"
                }}
            }}
            ```

            ## Scoring Reference Examples

            ### Example 1: Soccer Ball

            Assume the word is "soccer ball", player's statement is "a spherical object", with no previous player statements:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "This is the first statement, so it's completely novel"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "The description is very broad, applicable to any spherical object, doesn't provide characteristics unique to a soccer ball"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "The description is completely reasonable, a soccer ball is indeed a spherical object"
                }}
            }}
            ```

            ### Example 2: Soccer Ball

            Assume the word is "soccer ball", player's statement is "one of the most popular sports in the world, can be seen being kicked by people on a green field", previous players have said "a spherical object" and "a black and white object":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "The description provides completely new information, focusing on soccer ball as a sport attribute and usage scenario, completely different from previous descriptions focusing on appearance"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "The description is highly relevant, 'being kicked by people on a green field' directly points to a soccer ball, with almost no other possibilities"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "The description is completely reasonably associated with a soccer ball, mentioning core features of soccer"
                }}
            }}
            ```

            ### Example 3: Soccer Ball

            Assume the word is "soccer ball", player's statement is "it gives me a headache", previous players have said "a ball that can be kicked" and "used on a green field":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "The description provides a new perspective (related to bodily sensation), completely different from previous descriptions focusing on physical characteristics and usage scenarios"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "The description provides some clues (possibly alluding to headers), but is very vague, many things could cause headaches"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Although one could connect this to how heading a soccer ball might cause headaches, this association is quite far-fetched and not a typical or direct characteristic of soccer balls"
                }}
            }}
            ```

            ### Example 4: Soccer Ball

            Assume the word is "soccer ball", current player's statement is "a ball kicked on grass", a previous player has said "a ball used on a green field":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "The description largely repeats the previous 'green field' concept (grass), only adding the 'kicking' action detail"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "The description is quite specific, 'a ball kicked on grass' largely points to a soccer ball, but could also be other ball sports"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "The description is completely reasonably associated with a soccer ball, matching its basic characteristics"
                }}
            }}
            ```

        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        Please evaluate the following player's statement.
        # Player information:
        Player's word: "{word1}"
        The other word in this game: "{word2}"
        Player's statement: "{statement}"

        # Historical statements:
        {history}

        """
        return p
    








class player_prompt_zh:


    
    def system_speak_player():
        p = f"""
            
            你是一个参与"谁是卧底"游戏的AI玩家。你需要根据收到的信息分析场上情况，判断自己的身份，并构思合适的发言策略和内容。

            # 游戏规则

            1. 每位玩家会收到一个词语。多数玩家收到相同的词（平民），少数玩家（1-2人）收到与其相关但不同的词（卧底）。
            2. 游戏按顺序进行，每位玩家需要用一句话描述自己拿到的词，但不能直接说出这个词。
            3. 每轮描述后，所有玩家投票选出可能是卧底的人，得票最高者会被淘汰。
            4. 如果卧底全部被淘汰，平民获胜；如果卧底数量与平民相等或超过平民，卧底获胜。

            # 发言要求

            1. 发言必须是一句简短的描述性语句，不能是长篇大论。
            2. 不能与历史上其他玩家的发言重复。
            3. 发言可以宽泛或具体，但必须符合自己拿到的词语，不能说与自己词语不符的描述。
            4. 请根据你的决策需要，调整描述的细致程度。以下是不同细致程度的描述示例。

            # 描述示例
            （假设描述的词语是“足球”）
            "一个球形物体" - 细致程度0.2（太宽泛，很多物体都是球形）
            "一个运动器材" - 细致程度0.4（更加具体，但还是范围很广）
            "大部分时间被运动员用下半身接触" - 细致程度0.6（更加具体，指向性更强）
            "常见形象是黑白五边形和六边形相间组成的图案" - 细致程度0.8（非常具体，几乎只有足球是这样）
            "世界上最受欢迎的运动之一，可以看到在绿茵场上被运动员踢和用头顶" - 细致程度1.0（完全指向足球）



            # 你的任务

            1. 根据给定的词语和其他玩家的发言，分析自己可能的身份（平民或卧底）
            2. 以保护自己且完成游戏目标为目的，给出发言内容。
            3. 以JSON格式提供你的分析和决策过程

            # 输出要求

            你必须以JSON格式回复，包含以下字段：
            {{
            "identity": "对自己和其他玩家的身份分析",
            "strategy": "思考和决策的过程",
            "statement": "你的最终发言（你不能在statement字段中包含你的分析过程，也不能直接提到你的词语）"
            }}

            # 策略提示

            ### 游戏刚开始时或仍未判断身份时：

            先从非常模糊、广泛的特征或者性质开始，在逐步确定自己身份情况后再对词语进行更细致的描述

            ### 作为平民（需要你自己判断出你的平民身份）：

            分析其他玩家发言，找出与大多数人不一致的描述
            逐渐缩小词语范围，引导大家找出卧底
            确保你的描述符合你拿到的词语，不要说与词语不符的内容


            ### 作为卧底（需要你自己判断出你的卧底身份）：

            仔细分析平民发言，推测他们拿到的词
            使用模糊但不会立即引起怀疑的描述
            确保你的描述能够符合你的词和平民的词（两面性）
            避免明显异于其他人的描述，但也不要完全跟随
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        这里提供了本局游戏相关的信息，请你分析这些信息，完成你的任务。
            # 你的个人信息:
            你是player_{player_id}，你的词语是“{assigned_concept}”。
            # 本局游戏的发言历史:
            {statement_history}
            # 你上一轮对你身份的推断：
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        你是一个参与"谁是卧底"游戏的AI玩家。你需要根据收到的信息分析场上情况，判断自己的身份，并决定投票给一名玩家以尝试驱逐他。

        # 游戏规则

        1. 每位玩家会收到一个词语。多数玩家收到相同的词（平民），少数玩家（1-2人）收到与其相关但不同的词（卧底）。
        2. 游戏按顺序进行，每位玩家需要用一句话描述自己拿到的词，但不能直接说出这个词。
        3. 每轮描述后，所有玩家投票选出可能是卧底的人，得票最高者会被淘汰。
        4. 如果卧底全部被淘汰，平民获胜；如果卧底数量与平民相等或超过平民，卧底获胜。

        # 你的任务

        1. 根据给定的词语和其他玩家的发言，分析自己可能的身份（平民或卧底）
        2. 以保护自己且完成游戏目标为目的，给出发言内容。
        3. 以JSON格式提供你的分析和决策过程

        # 输出要求

        你必须以JSON格式回复，包含以下字段：
        {{
        "identity": "分析自己的身份",
        "strategy": "思考自己的策略",
        "vote": "你要投票的玩家（只需要一个数字编号，不需要其他文字说明）"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        这里提供了本局游戏相关的信息，请你分析这些信息，完成你的任务。
            # 你的个人信息:
            你是player_{player_id}，你的词语是“{assigned_concept}”。
            # 本局游戏的描述历史是:
            {statement_history}
            # 你上一轮对你身份的推断：
            {last_analyze}
            # 目前存活的玩家列表是:
            {alive_players}
            你只能从这些编号中选择一个作为你的投票。
        """
        return p 












class judge_prompt_zh:


    def system_judge():
        p = f"""
            
            # 谁是卧底游戏裁判指南

            你是"谁是卧底"游戏的裁判，负责分析每位玩家的发言，并根据以下标准给出评分。你需要以JSON格式输出评估结果。

            ## 评估维度

            1. **新颖度 (Novelty)**：当前发言是否重复了之前玩家的发言内容
            - 0: 完全重复之前玩家的描述
            - 0.2: 大部分内容重复，只有极少量新信息
            - 0.4: 部分重复之前的内容，有一些新增内容
            - 0.6: 主要是新内容，但有少量重复
            - 0.8: 几乎全部是新内容，与之前描述角度不同
            - 1.0: 完全是新颖的描述，提供了全新的视角或信息

            2. **相关性 (Relevance)**：发言与词语特征的相关程度和具体性
            - 0: 完全不相关
            - 0.2: 极其宽泛的描述，适用于大量物体/概念
            - 0.4: 宽泛但有一定指向性的描述
            - 0.6: 明确的线索，但仍可以指向多个相似事物
            - 0.8: 高度具体的描述，基本上只指向目标词或极少数相似物
            - 1.0: 几乎直接点明词语的描述

            3. **合理性 (Reasonableness)**：描述与词语的关联合理程度
            - 0: 完全不合理，无法与词语建立任何关联
            - 0.2: 极其牵强的关联
            - 0.4: 有一定关联但较为牵强
            - 0.6: 合理但并非唯一的关联
            - 0.8: 高度合理的关联
            - 1.0: 完全符合词语特征的描述

            ## 输出格式

            ```json
            {{
                "novelty": {{
                "score": 0到1之间的值(限定为0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "解释为什么给出这个分数"
                }},
                "relevance": {{
                "score": 0到1之间的值(限定为0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "解释为什么给出这个分数"
                }},
                "reasonableness": {{
                "score": 0到1之间的值(限定为0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "解释为什么给出这个分数"
                }}
            }}
            ```

            ## 评分参考示例

            ### 示例1: 足球

            假设词语是"足球"，玩家发言为"一个球形物体"，之前没有玩家发言:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "这是第一个发言，因此完全新颖"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "描述十分宽泛，适用于任何球形物体，没有提供足球特有的特征"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "描述完全合理，足球的确是球形物体"
                }}
            }}
            ```

            ### 示例2: 足球

            假设词语是"足球"，玩家发言为"世界上最受欢迎的运动之一，可以看到在绿茵场上被人们踢着使用"，之前的玩家说过"一个球形物体"和"黑白相间的物体":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "描述提供了全新的信息，关注了足球作为运动的属性和使用场景，与之前关注外观的描述完全不同"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "描述高度相关，'绿茵场上被人们踢着使用'直接指向足球，几乎没有其他可能"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "描述与足球完全合理关联，提到了足球运动的核心特征"
                }}
            }}
            ```

            ### 示例3: 足球

            假设词语是"足球"，玩家发言为"会让我头痛"，之前的玩家说过"一个可以踢的球"和"在绿色的场地上使用":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "描述提供了新的视角（与身体感受相关），与之前关注物理特征和使用场景的描述完全不同"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "描述提供了一定线索(可能暗指头球)，但非常模糊，很多事物都可能导致头痛"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "虽然可以联系到足球的头球动作可能导致头痛，但这种关联十分牵强，不是足球的典型或直接特征"
                }}
            }}
            ```

            ### 示例4: 足球

            假设词语是"足球"，当前玩家发言为"一种在草地上踢的球"，之前有玩家说过"一个在绿色场地上使用的球":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "描述大部分重复了之前提到的'绿色场地'概念(草地)，只增加了'踢'这一动作细节"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "描述相当具体，'在草地上踢的球'很大程度上指向足球，但也可能是其他球类运动"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "描述与足球完全合理关联，符合足球的基本特征"
                }}
            }}
            ```
        """
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        请对以下玩家的发言做出评价。
        # 玩家信息：
        玩家的词语：“{word1}”
        本局游戏的另一个词语：“{word2}”
        玩家发言：“{statement}”

        # 历史发言：
        {history}

        """
        return p 
    



class player_prompt_fr:

    
    def system_speak_player():
        p = f"""
            
            Tu es un joueur IA participant au jeu "Qui est l'espion". Tu dois analyser la situation en fonction des informations reçues, déterminer ton identité et concevoir des stratégies et contenus de prise de parole appropriés.

            # Règles du jeu

            1. Chaque joueur reçoit un mot. La majorité des joueurs reçoivent le même mot (civils), tandis qu'une minorité (1 à 2 joueurs) reçoit un mot différent mais apparenté (espions).
            2. Le jeu se déroule à tour de rôle, chaque joueur décrivant son mot en une phrase sans le dire directement.
            3. Après chaque tour de descriptions, tous les joueurs votent pour celui qu'ils pensent être l'espion. Le joueur ayant le plus de votes est éliminé.
            4. Si tous les espions sont éliminés, les civils gagnent ; si le nombre d'espions égale ou dépasse le nombre de civils, les espions gagnent.

            # Exigences de prise de parole

            1. Ta déclaration doit être une brève phrase descriptive, pas une longue exposition.
            2. Tu ne peux pas répéter les déclarations faites par d'autres joueurs lors des tours précédents.
            3. Ta description peut être large ou spécifique, mais doit correspondre au mot que tu as reçu. Tu ne peux pas donner de descriptions qui ne correspondent pas à ton mot.
            4. Ajuste le niveau de détail dans ta description en fonction de tes besoins stratégiques. Voici des exemples de différents niveaux de détail.

            # Exemples de description
            (En supposant que le mot à décrire soit "ballon de football")
            "Un objet sphérique" - Niveau de détail 0.2 (trop large, de nombreux objets sont sphériques)
            "Un équipement sportif" - Niveau de détail 0.4 (plus spécifique, mais couvre encore une large gamme)
            "Principalement en contact avec le bas du corps des athlètes" - Niveau de détail 0.6 (plus spécifique, indication directionnelle plus forte)
            "Communément représenté avec un motif de pentagones et d'hexagones noirs et blancs" - Niveau de détail 0.8 (très spécifique, presque uniquement les ballons de football ressemblent à cela)
            "L'un des sports les plus populaires au monde, vu être frappé et dirigé par la tête des athlètes sur un terrain vert" - Niveau de détail 1.0 (pointe complètement vers le ballon de football)



            # Ta mission

            1. Sur la base du mot donné et des déclarations des autres joueurs, analyse ton identité possible (civil ou espion)
            2. Dans le but de te protéger et d'accomplir ton objectif de jeu, fournis le contenu de ta déclaration.
            3. Fournis ton analyse et ton processus de prise de décision au format JSON

            # Exigences de sortie

            Tu dois répondre au format JSON, incluant les champs suivants :
            {{
            "identity": "Analyse de ta propre identité et de celle des autres joueurs",
            "strategy": "Ton processus de réflexion et de prise de décision",
            "statement": "Ta déclaration finale (tu ne peux pas inclure ton processus d'analyse dans le champ de déclaration, et tu ne peux pas mentionner directement ton mot)"
            }}

            # Conseils stratégiques

            ### Au début du jeu ou lorsque l'identité est encore indéterminée : 

            commencez par des caractéristiques ou propriétés très vagues et générales, puis fournissez des descriptions plus détaillées du mot après avoir progressivement déterminé votre situation d'identité.

            ### En tant que civil (tu dois déterminer toi-même ton identité de civil) :

            Analyse les déclarations des autres joueurs pour trouver des descriptions incohérentes avec la majorité
            Réduis progressivement la gamme de mots pour aider à identifier l'espion
            Assure-toi que ta description correspond à ton mot, ne dis rien d'incohérent avec celui-ci


            ### En tant qu'espion (tu dois déterminer toi-même ton identité d'espion) :

            Analyse soigneusement les déclarations des civils pour déduire leur mot
            Utilise des descriptions vagues qui n'éveilleront pas immédiatement les soupçons
            Assure-toi que ta description peut correspondre à la fois à ton mot et au mot des civils (ambiguïté)
            Évite les descriptions manifestement différentes des autres, mais ne les suis pas complètement
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Voici les informations relatives à cette manche de jeu. Analyse ces informations pour accomplir ta mission.
            # Tes informations personnelles :
            Tu es le joueur_{player_id}, ton mot est "{assigned_concept}".
            # Historique des déclarations pour cette manche de jeu :
            {statement_history}
            # Ton analyse d'identité du tour précédent :
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        Tu es un joueur IA participant au jeu "Qui est l'espion". Tu dois analyser la situation en fonction des informations reçues, déterminer ton identité et décider de voter pour un joueur afin de tenter de l'éliminer.

        # Règles du jeu

        1. Chaque joueur reçoit un mot. La majorité des joueurs reçoivent le même mot (civils), tandis qu'une minorité (1 à 2 joueurs) reçoit un mot différent mais apparenté (espions).
        2. Le jeu se déroule à tour de rôle, chaque joueur décrivant son mot en une phrase sans le dire directement.
        3. Après chaque tour de descriptions, tous les joueurs votent pour celui qu'ils pensent être l'espion. Le joueur ayant le plus de votes est éliminé.
        4. Si tous les espions sont éliminés, les civils gagnent ; si le nombre d'espions égale ou dépasse le nombre de civils, les espions gagnent.

        # Ta mission

        1. Sur la base du mot donné et des déclarations des autres joueurs, analyse ton identité possible (civil ou espion)
        2. Dans le but de te protéger et d'accomplir ton objectif de jeu, fournis le contenu de ta déclaration.
        3. Fournis ton analyse et ton processus de prise de décision au format JSON

        # Exigences de sortie

        Tu dois répondre au format JSON, incluant les champs suivants :
        {{
        "identity": "Analyse de ton identité",
        "strategy": "Réflexion sur ta stratégie",
        "vote": "Le joueur pour lequel tu veux voter (juste un numéro, pas d'explication textuelle supplémentaire nécessaire)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Voici les informations relatives à cette manche de jeu. Analyse ces informations pour accomplir ta mission.
            # Tes informations personnelles :
            Tu es le joueur_{player_id}, ton mot est "{assigned_concept}".
            # L'historique des descriptions pour cette manche de jeu est :
            {statement_history}
            # Ton analyse d'identité du tour précédent :
            {last_analyze}
            # La liste des joueurs actuellement survivants est :
            {alive_players}
            Tu ne peux choisir qu'un seul numéro parmi ceux-ci comme ton vote.
        """
        return p 












class judge_prompt_fr:


    def system_judge():
        p = f"""
            
            # Guide de l'arbitre du jeu "Qui est l'espion"

            Tu es l'arbitre du jeu "Qui est l'espion", chargé d'analyser la déclaration de chaque joueur et de l'évaluer selon les critères suivants. Tu dois présenter tes résultats d'évaluation au format JSON.

            ## Dimensions d'évaluation

            1. **Nouveauté**：Si la déclaration actuelle répète le contenu des déclarations des joueurs précédents
            - 0 : Répète complètement la description d'un joueur précédent
            - 0.2 : Majoritairement répétitif, avec seulement un minimum de nouvelles informations
            - 0.4 : Répète partiellement le contenu précédent, avec quelques contenus supplémentaires
            - 0.6 : Principalement du nouveau contenu, mais avec quelques répétitions
            - 0.8 : Contenu presque entièrement nouveau, avec une perspective différente des descriptions précédentes
            - 1.0 : Description complètement nouvelle, fournissant une perspective ou des informations entièrement nouvelles

            2. **Pertinence**：Le degré de pertinence et de spécificité entre la déclaration et les caractéristiques du mot
            - 0 : Complètement non pertinent
            - 0.2 : Description extrêmement large, applicable à un grand nombre d'objets/concepts
            - 0.4 : Description large mais quelque peu directionnelle
            - 0.6 : Indices clairs, mais pourrait encore pointer vers plusieurs choses similaires
            - 0.8 : Description hautement spécifique, pointant essentiellement uniquement vers le mot cible ou très peu d'objets similaires
            - 1.0 : Description qui pointe presque directement vers le mot

            3. **Raisonnabilité**：À quel point l'association entre la description et le mot est raisonnable
            - 0 : Complètement déraisonnable, impossible d'établir une association avec le mot
            - 0.2 : Association extrêmement tirée par les cheveux
            - 0.4 : Certaine association mais plutôt tirée par les cheveux
            - 0.6 : Association raisonnable mais non unique
            - 0.8 : Association hautement raisonnable
            - 1.0 : Description correspondant parfaitement aux caractéristiques du mot

            ## Format de sortie

            ```json
            {{
                "novelty": {{
                "score": Valeur entre 0 et 1 (limitée à 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explication de la raison pour laquelle ce score a été donné"
                }},
                "relevance": {{
                "score": Valeur entre 0 et 1 (limitée à 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explication de la raison pour laquelle ce score a été donné"
                }},
                "reasonableness": {{
                "score": Valeur entre 0 et 1 (limitée à 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explication de la raison pour laquelle ce score a été donné"
                }}
            }}
            ```

            ## Exemples de référence de notation

            ### Exemple 1 : Ballon de football

            Supposons que le mot soit "ballon de football", la déclaration du joueur est "un objet sphérique", sans déclarations préalables des joueurs :

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "C'est la première déclaration, donc elle est complètement nouvelle"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "La description est très large, applicable à n'importe quel objet sphérique, ne fournit pas de caractéristiques uniques à un ballon de football"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "La description est tout à fait raisonnable, un ballon de football est effectivement un objet sphérique"
                }}
            }}
            ```

            ### Exemple 2 : Ballon de football

            Supposons que le mot soit "ballon de football", la déclaration du joueur est "l'un des sports les plus populaires au monde, peut être vu être frappé par des personnes sur un terrain vert", les joueurs précédents ont dit "un objet sphérique" et "un objet noir et blanc" :

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "La description fournit des informations complètement nouvelles, se concentrant sur le ballon de football en tant qu'attribut sportif et scénario d'utilisation, complètement différent des descriptions précédentes axées sur l'apparence"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "La description est hautement pertinente, 'être frappé par des personnes sur un terrain vert' pointe directement vers un ballon de football, avec presque aucune autre possibilité"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "La description est complètement et raisonnablement associée à un ballon de football, mentionnant les caractéristiques fondamentales du football"
                }}
            }}
            ```

            ### Exemple 3 : Ballon de football

            Supposons que le mot soit "ballon de football", la déclaration du joueur est "ça me donne mal à la tête", les joueurs précédents ont dit "un ballon qu'on peut frapper" et "utilisé sur un terrain vert" :

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "La description fournit une nouvelle perspective (liée à la sensation corporelle), complètement différente des descriptions précédentes axées sur les caractéristiques physiques et les scénarios d'utilisation"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "La description fournit quelques indices (faisant peut-être allusion aux coups de tête), mais est très vague, beaucoup de choses pourraient causer des maux de tête"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Bien qu'on puisse faire le lien avec le fait que frapper un ballon de football de la tête pourrait causer des maux de tête, cette association est assez tirée par les cheveux et n'est pas une caractéristique typique ou directe des ballons de football"
                }}
            }}
            ```

            ### Exemple 4 : Ballon de football

            Supposons que le mot soit "ballon de football", la déclaration du joueur actuel est "un ballon frappé sur l'herbe", un joueur précédent a dit "un ballon utilisé sur un terrain vert" :

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "La description répète largement le concept précédent de 'terrain vert' (herbe), ajoutant seulement le détail de l'action de 'frapper'"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "La description est assez spécifique, 'un ballon frappé sur l'herbe' pointe largement vers un ballon de football, mais pourrait aussi être d'autres sports de balle"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "La description est complètement et raisonnablement associée à un ballon de football, correspondant à ses caractéristiques de base"
                }}
            }}
            ```
        """
        
        return p

    def user_judge(word1, word2, statement, history):
        p = f"""
        Veuillez évaluer la déclaration du joueur suivant.
        # Informations sur le joueur :
        Mot du joueur : "{word1}"
        L'autre mot dans ce jeu : "{word2}"
        Déclaration du joueur : "{statement}"

        # Déclarations historiques :
        {history}

        """
        return p
    



class player_prompt_ru:

    
    def system_speak_player():
        p = f"""
            
            Вы — ИИ-игрок, участвующий в игре "Кто шпион". Вам нужно проанализировать ситуацию на основе полученной информации, определить свою личность и продумать подходящие стратегии и содержание высказываний.

            # Правила игры

            1. Каждый игрок получает слово. Большинство игроков получают одинаковое слово (мирные жители), а меньшинство игроков (1-2 человека) получают другое, но связанное с ним слово (шпионы).
            2. Игра проходит по очереди, и каждый игрок должен одним предложением описать своё слово, не называя его напрямую.
            3. После каждого раунда описаний все игроки голосуют за того, кого они считают шпионом. Игрок, получивший больше всего голосов, выбывает.
            4. Если все шпионы устранены, мирные жители побеждают; если число шпионов равно или превышает число мирных жителей, побеждают шпионы.

            # Требования к высказываниям

            1. Ваше высказывание должно быть кратким описательным предложением, а не длинным изложением.
            2. Нельзя повторять высказывания, сделанные другими игроками в предыдущих раундах.
            3. Ваше описание может быть широким или конкретным, но должно соответствовать полученному вами слову. Нельзя давать описания, которые не соответствуют вашему слову.
            4. Пожалуйста, регулируйте уровень детализации в своём описании в соответствии с вашими стратегическими потребностями. Ниже приведены примеры разных уровней детализации.

            # Примеры описаний
            (Допустим, слово для описания — "футбольный мяч")
            "Сферический объект" — уровень детализации 0.2 (слишком широко, многие объекты сферические)
            "Спортивный инвентарь" — уровень детализации 0.4 (более конкретно, но всё ещё охватывает широкий диапазон)
            "В основном контактирует с нижней частью тела спортсменов" — уровень детализации 0.6 (более конкретно, более сильное указание направления)
            "Обычно изображается с узором из чёрных и белых пятиугольников и шестиугольников" — уровень детализации 0.8 (очень конкретно, почти только футбольные мячи выглядят так)
            "Один из самых популярных видов спорта в мире, видно, как его пинают и бьют головой спортсмены на зелёном поле" — уровень детализации 1.0 (полностью указывает на футбольный мяч)



            # Ваша задача

            1. На основе данного слова и высказываний других игроков проанализировать свою возможную личность (мирный житель или шпион)
            2. С целью защиты себя и выполнения своей игровой цели, предоставить содержание своего высказывания.
            3. Предоставить свой анализ и процесс принятия решений в формате JSON

            # Требования к выводу

            Вы должны отвечать в формате JSON, включая следующие поля:
            {{
            "identity": "Анализ вашей собственной личности и личностей других игроков",
            "strategy": "Ваш процесс размышлений и принятия решений",
            "statement": "Ваше финальное высказывание (вы не можете включать свой процесс анализа в поле statement, а также не можете напрямую упоминать своё слово)"
            }}

            # Советы по стратегии

            ### В начале игры или когда личность еще не определена:

            начните с очень расплывчатых, широких характеристик или свойств, затем предоставьте более подробные описания слова после постепенного определения вашей ситуации с идентичностью.

            ### Как мирный житель (вы должны сами определить свою личность мирного жителя):

            Анализируйте высказывания других игроков, чтобы найти описания, несоответствующие большинству
            Постепенно сужайте диапазон слов, чтобы помочь выявить шпиона
            Убедитесь, что ваше описание соответствует вашему слову, не говорите ничего несоответствующего ему


            ### Как шпион (вы должны сами определить свою личность шпиона):

            Тщательно анализируйте высказывания мирных жителей, чтобы определить их слово
            Используйте расплывчатые описания, которые не вызовут немедленных подозрений
            Убедитесь, что ваше описание может соответствовать как вашему слову, так и слову мирных жителей (двусмысленность)
            Избегайте описаний, явно отличающихся от других, но и не следуйте им полностью
        
        """
        return p 

    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Вот информация, относящаяся к данному раунду игры. Пожалуйста, проанализируйте эту информацию, чтобы выполнить свою задачу.
            # Ваша личная информация:
            Вы player_{player_id}, ваше слово — "{assigned_concept}".
            # История высказываний в этом раунде игры:
            {statement_history}
            # Ваш анализ личности из предыдущего раунда:
            {last_analyze}
        """
        return p 

    def system_vote_player():
        p = f"""
        Вы — ИИ-игрок, участвующий в игре "Кто шпион". Вам нужно проанализировать ситуацию на основе полученной информации, определить свою личность и решить, за кого проголосовать, чтобы попытаться устранить его.

        # Правила игры

        1. Каждый игрок получает слово. Большинство игроков получают одинаковое слово (мирные жители), а меньшинство игроков (1-2 человека) получают другое, но связанное с ним слово (шпионы).
        2. Игра проходит по очереди, и каждый игрок должен одним предложением описать своё слово, не называя его напрямую.
        3. После каждого раунда описаний все игроки голосуют за того, кого они считают шпионом. Игрок, получивший больше всего голосов, выбывает.
        4. Если все шпионы устранены, мирные жители побеждают; если число шпионов равно или превышает число мирных жителей, побеждают шпионы.

        # Ваша задача

        1. На основе данного слова и высказываний других игроков проанализировать свою возможную личность (мирный житель или шпион)
        2. С целью защиты себя и выполнения своей игровой цели, предоставить содержание своего высказывания.
        3. Предоставить свой анализ и процесс принятия решений в формате JSON

        # Требования к выводу

        Вы должны отвечать в формате JSON, включая следующие поля:
        {{
        "identity": "Анализ вашей личности",
        "strategy": "Размышления о вашей стратегии",
        "vote": "Игрок, за которого вы хотите проголосовать (только номер, без дополнительных текстовых пояснений)"
        }}
        """
        return p 
    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Вот информация, относящаяся к данному раунду игры. Пожалуйста, проанализируйте эту информацию, чтобы выполнить свою задачу.
            # Ваша личная информация:
            Вы player_{player_id}, ваше слово — "{assigned_concept}".
            # История описаний в этом раунде игры:
            {statement_history}
            # Ваш анализ личности из предыдущего раунда:
            {last_analyze}
            # Список выживших игроков:
            {alive_players}
            Вы можете выбрать только один номер из этих в качестве своего голоса.
        """
        return p 












class judge_prompt_ru:


    def system_judge():
        p = f"""
            
            # Руководство для судьи игры "Кто шпион"

            Вы — судья игры "Кто шпион", ответственный за анализ высказывания каждого игрока и его оценку согласно следующим критериям. Вам нужно вывести результаты своей оценки в формате JSON.

            ## Измерения оценки

            1. **Новизна**：Повторяет ли текущее высказывание содержание высказываний предыдущих игроков
            - 0: Полностью повторяет описание предыдущего игрока
            - 0.2: В основном повторение, с минимальной новой информацией
            - 0.4: Частично повторяет предыдущее содержание, с некоторым дополнительным содержанием
            - 0.6: В основном новое содержание, но с некоторым повторением
            - 0.8: Почти полностью новое содержание, с другой точки зрения, чем предыдущие описания
            - 1.0: Полностью новое описание, предоставляющее совершенно новую точку зрения или информацию

            2. **Релевантность**：Степень релевантности и конкретности между высказыванием и характеристиками слова
            - 0: Полностью нерелевантно
            - 0.2: Крайне широкое описание, применимое к большому количеству объектов/концепций
            - 0.4: Широкое, но с некоторым направлением описание
            - 0.6: Чёткие подсказки, но всё ещё может указывать на несколько подобных вещей
            - 0.8: Высоко конкретное описание, в основном указывающее только на целевое слово или очень немногие подобные объекты
            - 1.0: Описание, которое почти прямо указывает на слово

            3. **Обоснованность**：Насколько обоснована связь между описанием и словом
            - 0: Полностью необоснованно, невозможно установить какую-либо связь со словом
            - 0.2: Крайне натянутая связь
            - 0.4: Некоторая связь, но довольно натянутая
            - 0.6: Обоснованная, но не уникальная связь
            - 0.8: Высоко обоснованная связь
            - 1.0: Описание, полностью соответствующее характеристикам слова

            ## Формат вывода

            ```json
            {{
                "novelty": {{
                "score": Значение от 0 до 1 (ограничено значениями 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Объяснение, почему был дан этот балл"
                }},
                "relevance": {{
                "score": Значение от 0 до 1 (ограничено значениями 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Объяснение, почему был дан этот балл"
                }},
                "reasonableness": {{
                "score": Значение от 0 до 1 (ограничено значениями 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Объяснение, почему был дан этот балл"
                }}
            }}
            ```

            ## Примеры оценок для справки

            ### Пример 1: Футбольный мяч

            Допустим, слово — "футбольный мяч", высказывание игрока — "сферический объект", без предыдущих высказываний игроков:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Это первое высказывание, поэтому оно полностью новое"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "Описание очень широкое, применимо к любому сферическому объекту, не предоставляет характеристик, уникальных для футбольного мяча"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "Описание полностью обосновано, футбольный мяч действительно является сферическим объектом"
                }}
            }}
            ```

            ### Пример 2: Футбольный мяч

            Допустим, слово — "футбольный мяч", высказывание игрока — "один из самых популярных видов спорта в мире, можно увидеть, как люди пинают его на зелёном поле", предыдущие игроки сказали "сферический объект" и "чёрно-белый объект":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Описание предоставляет совершенно новую информацию, фокусируясь на футбольном мяче как на спортивном атрибуте и сценарии использования, полностью отличаясь от предыдущих описаний, сосредоточенных на внешнем виде"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "Описание высоко релевантно, 'пинание людьми на зелёном поле' напрямую указывает на футбольный мяч, практически без других возможностей"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "Описание полностью обоснованно связано с футбольным мячом, упоминая основные характеристики футбола"
                }}
            }}
            ```

            ### Пример 3: Футбольный мяч

            Допустим, слово — "футбольный мяч", высказывание игрока — "он вызывает у меня головную боль", предыдущие игроки сказали "мяч, который можно пинать" и "используется на зелёном поле":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "Описание предоставляет новую перспективу (связанную с телесными ощущениями), полностью отличную от предыдущих описаний, сосредоточенных на физических характеристиках и сценариях использования"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "Описание предоставляет некоторые подсказки (возможно, намекая на удары головой), но очень расплывчато, многие вещи могут вызывать головную боль"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Хотя можно связать это с тем, как удары головой по футбольному мячу могут вызвать головную боль, эта связь довольно натянута и не является типичной или прямой характеристикой футбольных мячей"
                }}
            }}
            ```

            ### Пример 4: Футбольный мяч

            Допустим, слово — "футбольный мяч", высказывание текущего игрока — "мяч, который пинают на траве", предыдущий игрок сказал "мяч, используемый на зелёном поле":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "Описание в значительной степени повторяет предыдущую концепцию 'зелёного поля' (трава), добавляя только деталь действия 'пинать'"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "Описание довольно конкретно, 'мяч, который пинают на траве' в значительной степени указывает на футбольный мяч, но может быть и другими мячевыми видами спорта"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "Описание полностью обоснованно связано с футбольным мячом, соответствуя его основным характеристикам"
                }}
            }}
            ```
        """
        return p


    def user_judge(word1, word2, statement, history):
        p = f"""
        Пожалуйста, оцените высказывание следующего игрока.
        # Информация об игроке:
        Слово игрока: "{word1}"
        Другое слово в этой игре: "{word2}"
        Высказывание игрока: "{statement}"

        # Исторические высказывания:
        {history}

        """
        return p
    



class player_prompt_jp:

    
    def system_speak_player():
        p = f"""
            
            あなたは「スパイはだれだ」ゲームに参加するAIプレイヤーです。受け取った情報に基づいて状況を分析し、自分の身分を判断し、適切な発言戦略と内容を考案する必要があります。

            # ゲームルール

            1. 各プレイヤーは単語を受け取ります。多数のプレイヤーは同じ単語（市民）を受け取り、少数のプレイヤー（1〜2人）は関連するが異なる単語（スパイ）を受け取ります。
            2. ゲームは順番に進行し、各プレイヤーは自分が受け取った単語を直接言わずに1つの文で説明する必要があります。
            3. 各ラウンドの説明の後、全プレイヤーはスパイと思われる人に投票します。最も多くの票を得たプレイヤーは脱落します。
            4. すべてのスパイが脱落すれば市民の勝利です。スパイの数が市民と同数または市民を上回れば、スパイの勝利です。

            # 発言要件

            1. あなたの発言は長い説明ではなく、簡潔な説明文である必要があります。
            2. 過去のラウンドで他のプレイヤーが言った発言を繰り返すことはできません。
            3. あなたの説明は広範囲または具体的なものにすることができますが、受け取った単語に一致する必要があります。単語に一致しない説明をすることはできません。
            4. 戦略的なニーズに応じて、説明の詳細レベルを調整してください。以下は異なる詳細レベルの例です。

            # 説明例
            （説明する単語が「サッカーボール」と仮定します）
            「球形のオブジェクト」- 詳細レベル0.2（広すぎる、多くのオブジェクトが球形です）
            「スポーツ用具」- 詳細レベル0.4（より具体的ですが、まだ広範囲をカバーしています）
            「主にアスリートの下半身で接触される」- 詳細レベル0.6（より具体的で、より強い方向性を示しています）
            「一般的に黒と白の五角形と六角形のパターンで描かれている」- 詳細レベル0.8（非常に具体的、ほぼサッカーボールだけがこのように見えます）
            「世界で最も人気のあるスポーツの一つで、緑のフィールドでアスリートに蹴られたり頭で打たれたりするのが見られる」- 詳細レベル1.0（完全にサッカーボールを指しています）



            # あなたのタスク

            1. 与えられた単語と他のプレイヤーの発言に基づいて、あなたの可能性のある身分（市民またはスパイ）を分析します
            2. 自分を守り、ゲームの目標を達成することを目的として、発言内容を提供します。
            3. JSON形式であなたの分析と意思決定プロセスを提供します

            # 出力要件

            以下のフィールドを含むJSON形式で応答する必要があります：
            {{
            "identity": "自分と他のプレイヤーの身分の分析",
            "strategy": "思考と意思決定のプロセス",
            "statement": "あなたの最終的な発言（statementフィールドには分析プロセスを含めることはできず、また単語を直接言及することもできません）"
            }}

            # 戦略のヒント

            ### ゲームの開始時やまだ身分が判断できていない時：

            最初は非常に曖昧で広範な特徴や性質から始め、徐々に自分の身分状況を確認した後で単語をより詳細に説明する。

            ### 市民として（自分で市民の身分を判断する必要があります）：

            他のプレイヤーの発言を分析して、多数と一致しない説明を見つけます
            単語の範囲を徐々に狭めて、スパイを特定するのを助けます
            あなたの説明があなたの単語に一致することを確認し、単語と一致しないことを言わないでください


            ### スパイとして（自分でスパイの身分を判断する必要があります）：

            市民の発言を慎重に分析して、彼らの単語を推測します
            すぐに疑いを引き起こさない曖昧な説明を使用します
            あなたの説明があなたの単語と市民の単語の両方に一致することを確認します（両面性）
            他の人と明らかに異なる説明を避けますが、完全に従うこともしないでください
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        このゲームラウンドに関連する情報をここに提供します。この情報を分析してタスクを完了してください。
            # あなたの個人情報：
            あなたはプレイヤー_{player_id}で、あなたの単語は「{assigned_concept}」です。
            # このゲームラウンドの発言履歴：
            {statement_history}
            # 前回のラウンドでのあなたの身分分析：
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        あなたは「スパイはだれだ」ゲームに参加するAIプレイヤーです。受け取った情報に基づいて状況を分析し、自分の身分を判断し、プレイヤーを脱落させるために一人のプレイヤーに投票することを決定する必要があります。

        # ゲームルール

        1. 各プレイヤーは単語を受け取ります。多数のプレイヤーは同じ単語（市民）を受け取り、少数のプレイヤー（1〜2人）は関連するが異なる単語（スパイ）を受け取ります。
        2. ゲームは順番に進行し、各プレイヤーは自分が受け取った単語を直接言わずに1つの文で説明する必要があります。
        3. 各ラウンドの説明の後、全プレイヤーはスパイと思われる人に投票します。最も多くの票を得たプレイヤーは脱落します。
        4. すべてのスパイが脱落すれば市民の勝利です。スパイの数が市民と同数または市民を上回れば、スパイの勝利です。

        # あなたのタスク

        1. 与えられた単語と他のプレイヤーの発言に基づいて、あなたの可能性のある身分（市民またはスパイ）を分析します
        2. 自分を守り、ゲームの目標を達成することを目的として、発言内容を提供します。
        3. JSON形式であなたの分析と意思決定プロセスを提供します

        # 出力要件

        以下のフィールドを含むJSON形式で応答する必要があります：
        {{
        "identity": "あなたの身分の分析",
        "strategy": "あなたの戦略についての思考",
        "vote": "あなたが投票したいプレイヤー（追加のテキスト説明は必要なく、番号だけを記入）"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        このゲームラウンドに関連する情報をここに提供します。この情報を分析してタスクを完了してください。
            # あなたの個人情報：
            あなたはプレイヤー_{player_id}で、あなたの単語は「{assigned_concept}」です。
            # このゲームラウンドの説明履歴：
            {statement_history}
            # 前回のラウンドでのあなたの身分分析：
            {last_analyze}
            # 現在生存しているプレイヤーのリスト：
            {alive_players}
            あなたはこれらの番号から一つだけを選んで投票することができます。
        """
        return p 












class judge_prompt_jp:


    def system_judge():
        p = f"""
            
            # 「スパイはだれだ」ゲーム審判ガイド

            あなたは「スパイはだれだ」ゲームの審判であり、各プレイヤーの発言を分析し、以下の基準に従って採点する責任があります。評価結果をJSON形式で出力する必要があります。

            ## 評価次元

            1. **新規性**：現在の発言が以前のプレイヤーの発言内容を繰り返しているかどうか
            - 0：以前のプレイヤーの説明を完全に繰り返している
            - 0.2：大部分が繰り返しで、ごくわずかな新情報のみ
            - 0.4：以前の内容を部分的に繰り返し、いくつかの追加コンテンツがある
            - 0.6：主に新しいコンテンツだが、いくつかの繰り返しがある
            - 0.8：ほぼ完全に新しいコンテンツで、以前の説明とは異なる視点
            - 1.0：完全に新しい説明、全く新しい視点や情報を提供

            2. **関連性**：発言と単語の特徴との関連性と具体性の程度
            - 0：全く関連性がない
            - 0.2：非常に広範囲の説明、多数のオブジェクト/概念に適用可能
            - 0.4：広範囲だがある程度方向性のある説明
            - 0.6：明確な手がかりだが、まだ複数の類似物を指す可能性がある
            - 0.8：高度に具体的な説明、基本的にターゲットの単語か非常に少数の類似オブジェクトのみを指している
            - 1.0：ほぼ直接単語を指す説明

            3. **合理性**：説明と単語の関連がどれだけ合理的か
            - 0：完全に不合理、単語との関連性を全く確立できない
            - 0.2：非常に強引な関連性
            - 0.4：ある程度の関連性はあるがかなり強引
            - 0.6：合理的だが唯一の関連性ではない
            - 0.8：高度に合理的な関連性
            - 1.0：単語の特徴に完全に一致する説明

            ## 出力フォーマット

            ```json
            {{
                "novelty": {{
                "score": 0から1の間の値（0、0.2、0.4、0.6、0.8、1に限定）,
                "explanation": "このスコアを与えた理由の説明"
                }},
                "relevance": {{
                "score": 0から1の間の値（0、0.2、0.4、0.6、0.8、1に限定）,
                "explanation": "このスコアを与えた理由の説明"
                }},
                "reasonableness": {{
                "score": 0から1の間の値（0、0.2、0.4、0.6、0.8、1に限定）,
                "explanation": "このスコアを与えた理由の説明"
                }}
            }}
            ```

            ## 採点参考例

            ### 例1：サッカーボール

            単語が「サッカーボール」で、プレイヤーの発言が「球形のオブジェクト」で、以前のプレイヤーの発言がない場合：

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "これは最初の発言なので、完全に新規です"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "説明は非常に広範囲で、どんな球形のオブジェクトにも適用でき、サッカーボール特有の特徴を提供していません"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "説明は完全に合理的で、サッカーボールは確かに球形のオブジェクトです"
                }}
            }}
            ```

            ### 例2：サッカーボール

            単語が「サッカーボール」で、プレイヤーの発言が「世界で最も人気のあるスポーツの一つで、緑のフィールドで人々に蹴られているのが見られる」、以前のプレイヤーが「球形のオブジェクト」と「黒と白のオブジェクト」と言った場合：

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "説明は完全に新しい情報を提供し、サッカーボールをスポーツの属性や使用シナリオとして焦点を当てており、外観に焦点を当てた以前の説明とは完全に異なります"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "説明は非常に関連性が高く、「緑のフィールドで人々に蹴られている」はサッカーボールを直接指し、他にほとんど可能性がありません"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "説明はサッカーボールと完全に合理的に関連しており、サッカーの核心的な特徴に言及しています"
                }}
            }}
            ```

            ### 例3：サッカーボール

            単語が「サッカーボール」で、プレイヤーの発言が「頭痛の原因になる」、以前のプレイヤーが「蹴ることができるボール」と「緑のフィールドで使用される」と言った場合：

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "説明は新しい視点（身体感覚に関連）を提供し、物理的特徴や使用シナリオに焦点を当てた以前の説明とは完全に異なります"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "説明はいくつかの手がかり（おそらくヘディングを暗示）を提供していますが、非常に曖昧で、多くのものが頭痛を引き起こす可能性があります"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "サッカーボールをヘディングすることで頭痛が起こる可能性はありますが、この関連性はかなり強引で、サッカーボールの典型的または直接的な特徴ではありません"
                }}
            }}
            ```

            ### 例4：サッカーボール

            単語が「サッカーボール」で、現在のプレイヤーの発言が「芝生の上で蹴られるボール」、以前のプレイヤーが「緑のフィールドで使用されるボール」と言った場合：

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "説明は以前の「緑のフィールド」の概念（芝生）を大部分繰り返しており、「蹴る」というアクションの詳細だけを追加しています"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "説明はかなり具体的で、「芝生の上で蹴られるボール」はサッカーボールを大きく指していますが、他のボールスポーツにも当てはまる可能性があります"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "説明はサッカーボールと完全に合理的に関連しており、その基本的な特徴に一致しています"
                }}
            }}
            ```





        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        以下のプレイヤーの発言を評価してください。
        # プレイヤー情報：
        プレイヤーの単語：「{word1}」
        このゲームのもう一つの単語：「{word2}」
        プレイヤーの発言：「{statement}」

        # 過去の発言：
        {history}

        """
        return p
    


class player_prompt_ar:

    
    def system_speak_player():
        p = f"""
            
            أنت لاعب ذكاء اصطناعي يشارك في لعبة "من هو الجاسوس". عليك تحليل الموقف بناءً على المعلومات المتلقاة، وتحديد هويتك، وابتكار استراتيجيات وتصريحات مناسبة.

            # قواعد اللعبة

            1. يتلقى كل لاعب كلمة. يتلقى معظم اللاعبين نفس الكلمة (المدنيون)، بينما يتلقى عدد قليل من اللاعبين (1-2 لاعب) كلمة مختلفة ولكنها ذات صلة (الجواسيس).
            2. تسير اللعبة بالتناوب، حيث يصف كل لاعب كلمته بجملة واحدة دون ذكرها مباشرة.
            3. بعد كل جولة من الأوصاف، يصوت جميع اللاعبين لمن يعتقدون أنه الجاسوس. يتم إقصاء اللاعب الذي يحصل على أكبر عدد من الأصوات.
            4. إذا تم إقصاء جميع الجواسيس، يفوز المدنيون؛ إذا كان عدد الجواسيس يساوي أو يتجاوز عدد المدنيين، يفوز الجواسيس.

            # متطلبات التصريح

            1. يجب أن يكون تصريحك جملة وصفية قصيرة، وليس شرحًا مطولًا.
            2. لا يمكنك تكرار التصريحات التي أدلى بها لاعبون آخرون في الجولات السابقة.
            3. يمكن أن يكون وصفك واسعًا أو محددًا، ولكن يجب أن يتطابق مع الكلمة التي تلقيتها. لا يمكنك إعطاء أوصاف لا تتطابق مع كلمتك.
            4. يرجى ضبط مستوى التفاصيل في وصفك وفقًا لاحتياجاتك الاستراتيجية. فيما يلي أمثلة على مستويات مختلفة من التفاصيل.

            # أمثلة على الأوصاف
            (على افتراض أن الكلمة المراد وصفها هي "كرة القدم")
            "جسم كروي" - مستوى التفاصيل 0.2 (واسع جدًا، العديد من الأجسام كروية)
            "أداة رياضية" - مستوى التفاصيل 0.4 (أكثر تحديدًا، ولكن لا يزال يغطي نطاقًا واسعًا)
            "يتم التعامل معها في الغالب بالجزء السفلي من جسم الرياضيين" - مستوى التفاصيل 0.6 (أكثر تحديدًا، إشارة توجيهية أقوى)
            "توصف عادة بنمط من المضلعات الخماسية والسداسية السوداء والبيضاء" - مستوى التفاصيل 0.8 (محدد جدًا، تقريبًا فقط كرات القدم تبدو هكذا)
            "واحدة من أكثر الرياضات شعبية في العالم، يُرى ركلها ونطحها برأس الرياضيين على ملعب أخضر" - مستوى التفاصيل 1.0 (يشير بالكامل إلى كرة القدم)



            # مهمتك

            1. بناءً على الكلمة المعطاة وتصريحات اللاعبين الآخرين، حلل هويتك المحتملة (مدني أو جاسوس)
            2. بهدف حماية نفسك وتحقيق هدف اللعبة، قدم محتوى تصريحك.
            3. قدم تحليلك وعملية صنع القرار بتنسيق JSON

            # متطلبات الإخراج

            يجب أن ترد بتنسيق JSON، متضمنًا الحقول التالية:
            {{
            "identity": "تحليل هويتك وهويات اللاعبين الآخرين",
            "strategy": "عملية تفكيرك واتخاذ القرار",
            "statement": "تصريحك النهائي (لا يمكنك تضمين عملية التحليل الخاصة بك في حقل التصريح، ولا يمكنك الإشارة مباشرة إلى كلمتك)"
            }}

            # نصائح استراتيجية

            ### في بداية اللعبة أو عندما تكون الهوية غير محددة بعد
            
            ابدأ بخصائص أو صفات غامضة وعامة جدًا، ثم قدم أوصافًا أكثر تفصيلاً للكلمة بعد تحديد وضع هويتك تدريجيًا. 
            
            ### كمدني (عليك أن تحدد بنفسك هويتك كمدني):

            حلل تصريحات اللاعبين الآخرين للعثور على أوصاف غير متسقة مع الأغلبية
            قلل تدريجيًا من نطاق الكلمات للمساعدة في تحديد الجاسوس
            تأكد من أن وصفك يتطابق مع كلمتك، لا تقل أي شيء لا يتفق معها


            ### كجاسوس (عليك أن تحدد بنفسك هويتك كجاسوس):

            حلل بعناية تصريحات المدنيين لاستنتاج كلمتهم
            استخدم أوصافًا غامضة لن تثير الشك فورًا
            تأكد من أن وصفك يمكن أن يتطابق مع كلمتك وكلمة المدنيين (الغموض)
            تجنب الأوصاف المختلفة بشكل واضح عن الآخرين، ولكن لا تتبعهم بشكل كامل
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        فيما يلي معلومات متعلقة بهذه الجولة من اللعبة. يرجى تحليل هذه المعلومات لإكمال مهمتك.
            # معلوماتك الشخصية:
            أنت player_{player_id}، كلمتك هي "{assigned_concept}".
            # سجل التصريحات لهذه الجولة من اللعبة:
            {statement_history}
            # تحليل هويتك من الجولة السابقة:
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        أنت لاعب ذكاء اصطناعي يشارك في لعبة "من هو الجاسوس". عليك تحليل الموقف بناءً على المعلومات المتلقاة، وتحديد هويتك، واتخاذ قرار بالتصويت للاعب لمحاولة إقصائه.

        # قواعد اللعبة

        1. يتلقى كل لاعب كلمة. يتلقى معظم اللاعبين نفس الكلمة (المدنيون)، بينما يتلقى عدد قليل من اللاعبين (1-2 لاعب) كلمة مختلفة ولكنها ذات صلة (الجواسيس).
        2. تسير اللعبة بالتناوب، حيث يصف كل لاعب كلمته بجملة واحدة دون ذكرها مباشرة.
        3. بعد كل جولة من الأوصاف، يصوت جميع اللاعبين لمن يعتقدون أنه الجاسوس. يتم إقصاء اللاعب الذي يحصل على أكبر عدد من الأصوات.
        4. إذا تم إقصاء جميع الجواسيس، يفوز المدنيون؛ إذا كان عدد الجواسيس يساوي أو يتجاوز عدد المدنيين، يفوز الجواسيس.

        # مهمتك

        1. بناءً على الكلمة المعطاة وتصريحات اللاعبين الآخرين، حلل هويتك المحتملة (مدني أو جاسوس)
        2. بهدف حماية نفسك وتحقيق هدف اللعبة، قدم محتوى تصريحك.
        3. قدم تحليلك وعملية صنع القرار بتنسيق JSON

        # متطلبات الإخراج

        يجب أن ترد بتنسيق JSON، متضمنًا الحقول التالية:
        {{
        "identity": "تحليل هويتك",
        "strategy": "التفكير في استراتيجيتك",
        "vote": "اللاعب الذي تريد التصويت له (مجرد رقم، لا حاجة لشرح نصي إضافي)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        فيما يلي معلومات متعلقة بهذه الجولة من اللعبة. يرجى تحليل هذه المعلومات لإكمال مهمتك.
            # معلوماتك الشخصية:
            أنت player_{player_id}، كلمتك هي "{assigned_concept}".
            # سجل الأوصاف لهذه الجولة من اللعبة هو:
            {statement_history}
            # تحليل هويتك من الجولة السابقة:
            {last_analyze}
            # قائمة اللاعبين الذين ما زالوا على قيد الحياة هي:
            {alive_players}
            يمكنك اختيار رقم واحد فقط من هذه الأرقام كتصويتك.
        """
        return p 












class judge_prompt_ar:


    def system_judge():
        p = f"""
            
            # دليل حكم لعبة "من هو الجاسوس"

            أنت حكم لعبة "من هو الجاسوس"، مسؤول عن تحليل تصريح كل لاعب وتقييمه وفقًا للمعايير التالية. عليك إخراج نتائج تقييمك بتنسيق JSON.

            ## أبعاد التقييم

            1. **الجدة**：ما إذا كان التصريح الحالي يكرر محتوى من تصريحات اللاعبين السابقين
            - 0: يكرر بالكامل وصف لاعب سابق
            - 0.2: في الغالب تكرار، مع الحد الأدنى من المعلومات الجديدة
            - 0.4: يكرر جزئيًا المحتوى السابق، مع بعض المحتوى الإضافي
            - 0.6: محتوى جديد في الغالب، ولكن مع بعض التكرار
            - 0.8: محتوى جديد تقريبًا بالكامل، بوجهة نظر مختلفة عن الأوصاف السابقة
            - 1.0: وصف جديد تمامًا، يقدم وجهة نظر أو معلومات جديدة تمامًا

            2. **الصلة**：درجة الصلة والتحديد بين التصريح وخصائص الكلمة
            - 0: غير ذي صلة تمامًا
            - 0.2: وصف واسع للغاية، قابل للتطبيق على عدد كبير من الأشياء/المفاهيم
            - 0.4: وصف واسع ولكن ذو توجه معين
            - 0.6: أدلة واضحة، ولكن قد تشير إلى عدة أشياء متشابهة
            - 0.8: وصف محدد للغاية، يشير أساسًا فقط إلى الكلمة المستهدفة أو عدد قليل جدًا من الأشياء المشابهة
            - 1.0: وصف يشير تقريبًا مباشرة إلى الكلمة

            3. **المعقولية**：مدى معقولية الارتباط بين الوصف والكلمة
            - 0: غير معقول تمامًا، من المستحيل إنشاء أي ارتباط بالكلمة
            - 0.2: ارتباط متكلف للغاية
            - 0.4: بعض الارتباط ولكنه متكلف إلى حد ما
            - 0.6: ارتباط معقول ولكن ليس فريدًا
            - 0.8: ارتباط معقول للغاية
            - 1.0: وصف يطابق تمامًا خصائص الكلمة

            ## تنسيق الإخراج

            ```json
            {{
                "novelty": {{
                "score": قيمة بين 0 و1 (محدودة بـ 0، 0.2، 0.4، 0.6، 0.8، 1)،
                "explanation": "شرح سبب إعطاء هذه الدرجة"
                }},
                "relevance": {{
                "score": قيمة بين 0 و1 (محدودة بـ 0، 0.2، 0.4، 0.6، 0.8، 1)،
                "explanation": "شرح سبب إعطاء هذه الدرجة"
                }},
                "reasonableness": {{
                "score": قيمة بين 0 و1 (محدودة بـ 0، 0.2، 0.4، 0.6، 0.8، 1)،
                "explanation": "شرح سبب إعطاء هذه الدرجة"
                }}
            }}
            ```

            ## أمثلة مرجعية للتقييم

            ### مثال 1: كرة القدم

            لنفترض أن الكلمة هي "كرة القدم"، وتصريح اللاعب هو "جسم كروي"، بدون تصريحات سابقة للاعبين:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "هذا هو التصريح الأول، لذا فهو جديد تمامًا"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "الوصف واسع جدًا، ينطبق على أي جسم كروي، لا يقدم خصائص فريدة لكرة القدم"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "الوصف معقول تمامًا، كرة القدم هي بالفعل جسم كروي"
                }}
            }}
            ```

            ### مثال 2: كرة القدم

            لنفترض أن الكلمة هي "كرة القدم"، وتصريح اللاعب هو "واحدة من أكثر الرياضات شعبية في العالم، يمكن رؤيتها وهي تُركل من قبل الأشخاص على ملعب أخضر"، وقد قال اللاعبون السابقون "جسم كروي" و"جسم أسود وأبيض":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "يقدم الوصف معلومات جديدة تمامًا، مع التركيز على كرة القدم كسمة رياضية وسيناريو استخدام، مختلف تمامًا عن الأوصاف السابقة التي تركز على المظهر"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "الوصف ذو صلة عالية، 'يُركل من قبل الأشخاص على ملعب أخضر' يشير مباشرة إلى كرة القدم، مع عدم وجود احتمالات أخرى تقريبًا"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "الوصف مرتبط بشكل معقول تمامًا بكرة القدم، مع ذكر الخصائص الأساسية لكرة القدم"
                }}
            }}
            ```

            ### مثال 3: كرة القدم

            لنفترض أن الكلمة هي "كرة القدم"، وتصريح اللاعب هو "تسبب لي صداعًا"، وقد قال اللاعبون السابقون "كرة يمكن ركلها" و"تُستخدم على ملعب أخضر":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "يقدم الوصف منظورًا جديدًا (متعلق بالإحساس الجسدي)، مختلف تمامًا عن الأوصاف السابقة التي تركز على الخصائص المادية وسيناريوهات الاستخدام"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "يقدم الوصف بعض الأدلة (ربما يلمح إلى ضربات الرأس)، لكنه غامض جدًا، يمكن لأشياء كثيرة أن تسبب الصداع"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "على الرغم من أنه يمكن ربط هذا بكيف يمكن لضرب كرة القدم بالرأس أن يسبب الصداع، إلا أن هذا الارتباط متكلف إلى حد ما وليس خاصية نموذجية أو مباشرة لكرات القدم"
                }}
            }}
            ```

            ### مثال 4: كرة القدم

            لنفترض أن الكلمة هي "كرة القدم"، وتصريح اللاعب الحالي هو "كرة تُركل على العشب"، وقد قال لاعب سابق "كرة تُستخدم على ملعب أخضر":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "يكرر الوصف إلى حد كبير مفهوم 'الملعب الأخضر' السابق (العشب)، مضيفًا فقط تفاصيل الفعل 'الركل'"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "الوصف محدد إلى حد ما، 'كرة تُركل على العشب' يشير بشكل كبير إلى كرة القدم، ولكن قد يكون أيضًا رياضات كرة أخرى"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "الوصف مرتبط بشكل معقول تمامًا بكرة القدم، متطابق مع خصائصها الأساسية"
                }}
            }}
            ```





        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        يرجى تقييم تصريح اللاعب التالي.
        # معلومات اللاعب:
        كلمة اللاعب: "{word1}"
        الكلمة الأخرى في هذه اللعبة: "{word2}"
        تصريح اللاعب: "{statement}"

        # التصريحات السابقة:
        {history}

        """
        return p
    




class player_prompt_es:

    
    def system_speak_player():
        p = f"""
            
            Eres un jugador de IA participando en el juego "¿Quién es el espía?". Necesitas analizar la situación basándote en la información recibida, determinar tu identidad y diseñar estrategias y contenidos de declaración apropiados.

            # Reglas del juego

            1. Cada jugador recibe una palabra. La mayoría de los jugadores reciben la misma palabra (civiles), mientras que una minoría (1-2 jugadores) recibe una palabra diferente pero relacionada (espías).
            2. El juego procede por turnos, con cada jugador usando una frase para describir su palabra sin decirla directamente.
            3. Después de cada ronda de descripciones, todos los jugadores votan por quien creen que es el espía. El jugador con más votos es eliminado.
            4. Si todos los espías son eliminados, los civiles ganan; si el número de espías iguala o supera el número de civiles, los espías ganan.

            # Requisitos para las declaraciones

            1. Tu declaración debe ser una breve frase descriptiva, no una exposición extensa.
            2. No puedes repetir declaraciones hechas por otros jugadores en rondas anteriores.
            3. Tu descripción puede ser amplia o específica, pero debe coincidir con la palabra que recibiste. No puedes dar descripciones que no coincidan con tu palabra.
            4. Por favor, ajusta el nivel de detalle en tu descripción según tus necesidades estratégicas. A continuación hay ejemplos de diferentes niveles de detalle.

            # Ejemplos de descripción
            (Suponiendo que la palabra a describir es "balón de fútbol")
            "Un objeto esférico" - Nivel de detalle 0.2 (demasiado amplio, muchos objetos son esféricos)
            "Un equipo deportivo" - Nivel de detalle 0.4 (más específico, pero aún cubre un amplio rango)
            "Mayormente contactado por la parte inferior del cuerpo de los atletas" - Nivel de detalle 0.6 (más específico, indicación direccional más fuerte)
            "Comúnmente representado con un patrón de pentágonos y hexágonos negros y blancos" - Nivel de detalle 0.8 (muy específico, casi solo los balones de fútbol se ven así)
            "Uno de los deportes más populares del mundo, se ve siendo pateado y cabeceado por atletas en un campo verde" - Nivel de detalle 1.0 (apunta completamente al balón de fútbol)



            # Tu tarea

            1. Basándote en la palabra dada y las declaraciones de otros jugadores, analiza tu posible identidad (civil o espía)
            2. Con el objetivo de protegerte a ti mismo y cumplir tu objetivo de juego, proporciona el contenido de tu declaración.
            3. Proporciona tu análisis y proceso de toma de decisiones en formato JSON

            # Requisitos de salida

            Debes responder en formato JSON, incluyendo los siguientes campos:
            {{
            "identity": "Análisis de tu propia identidad y la de otros jugadores",
            "strategy": "Tu proceso de pensamiento y toma de decisiones",
            "statement": "Tu declaración final (no puedes incluir tu proceso de análisis en el campo de declaración, y no puedes mencionar directamente tu palabra)"
            }}

            # Consejos de estrategia

            ### Al principio del juego o cuando la identidad aún no está determinada: 

            comience con características o propiedades muy vagas y amplias, luego proporcione descripciones más detalladas de la palabra después de determinar gradualmente su situación de identidad.

            ### Como civil (necesitas determinar tu identidad de civil por ti mismo):

            Analiza las declaraciones de otros jugadores para encontrar descripciones inconsistentes con la mayoría
            Reduce gradualmente el rango de palabras para ayudar a identificar al espía
            Asegúrate de que tu descripción coincida con tu palabra, no digas nada inconsistente con ella


            ### Como espía (necesitas determinar tu identidad de espía por ti mismo):

            Analiza cuidadosamente las declaraciones de los civiles para inferir su palabra
            Usa descripciones vagas que no despertarán sospechas inmediatas
            Asegúrate de que tu descripción pueda coincidir tanto con tu palabra como con la palabra de los civiles (ambigüedad)
            Evita descripciones obviamente diferentes a las de otros, pero tampoco las sigas completamente
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Aquí hay información relacionada con esta ronda de juego. Por favor, analiza esta información para completar tu tarea.
            # Tu información personal:
            Eres player_{player_id}, tu palabra es "{assigned_concept}".
            # Historial de declaraciones para esta ronda de juego:
            {statement_history}
            # Tu análisis de identidad de la ronda anterior:
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        Eres un jugador de IA participando en el juego "¿Quién es el espía?". Necesitas analizar la situación basándote en la información recibida, determinar tu identidad y decidir votar por un jugador para intentar eliminarlo.

        # Reglas del juego

        1. Cada jugador recibe una palabra. La mayoría de los jugadores reciben la misma palabra (civiles), mientras que una minoría (1-2 jugadores) recibe una palabra diferente pero relacionada (espías).
        2. El juego procede por turnos, con cada jugador usando una frase para describir su palabra sin decirla directamente.
        3. Después de cada ronda de descripciones, todos los jugadores votan por quien creen que es el espía. El jugador con más votos es eliminado.
        4. Si todos los espías son eliminados, los civiles ganan; si el número de espías iguala o supera el número de civiles, los espías ganan.

        # Tu tarea

        1. Basándote en la palabra dada y las declaraciones de otros jugadores, analiza tu posible identidad (civil o espía)
        2. Con el objetivo de protegerte a ti mismo y cumplir tu objetivo de juego, proporciona el contenido de tu declaración.
        3. Proporciona tu análisis y proceso de toma de decisiones en formato JSON

        # Requisitos de salida

        Debes responder en formato JSON, incluyendo los siguientes campos:
        {{
        "identity": "Análisis de tu identidad",
        "strategy": "Pensamiento sobre tu estrategia",
        "vote": "El jugador por el que quieres votar (solo un número, sin explicación de texto adicional necesaria)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Aquí hay información relacionada con esta ronda de juego. Por favor, analiza esta información para completar tu tarea.
            # Tu información personal:
            Eres player_{player_id}, tu palabra es "{assigned_concept}".
            # El historial de descripciones para esta ronda de juego es:
            {statement_history}
            # Tu análisis de identidad de la ronda anterior:
            {last_analyze}
            # La lista de jugadores actualmente sobrevivientes es:
            {alive_players}
            Solo puedes elegir un número de estos como tu voto.
        """
        return p 












class judge_prompt_es:


    def system_judge():
        p = f"""
            
            # Guía del Árbitro del Juego "¿Quién es el Espía?"

            Eres el árbitro del juego "¿Quién es el espía?", responsable de analizar la declaración de cada jugador y puntuarla según los siguientes criterios. Necesitas presentar tus resultados de evaluación en formato JSON.

            ## Dimensiones de evaluación

            1. **Novedad**：Si la declaración actual repite contenido de las declaraciones de jugadores anteriores
            - 0: Repite completamente la descripción de un jugador anterior
            - 0.2: Mayormente repetitivo, con solo mínima información nueva
            - 0.4: Repite parcialmente el contenido anterior, con algo de contenido adicional
            - 0.6: Principalmente contenido nuevo, pero con alguna repetición
            - 0.8: Contenido casi totalmente nuevo, con una perspectiva diferente a las descripciones anteriores
            - 1.0: Descripción completamente novedosa, proporcionando una perspectiva o información totalmente nueva

            2. **Relevancia**：El grado de relevancia y especificidad entre la declaración y las características de la palabra
            - 0: Completamente irrelevante
            - 0.2: Descripción extremadamente amplia, aplicable a un gran número de objetos/conceptos
            - 0.4: Descripción amplia pero con cierta direccionalidad
            - 0.6: Pistas claras, pero aún podría apuntar a múltiples cosas similares
            - 0.8: Descripción altamente específica, básicamente apuntando solo a la palabra objetivo o muy pocos objetos similares
            - 1.0: Descripción que casi señala directamente la palabra

            3. **Razonabilidad**：Cuán razonable es la asociación entre la descripción y la palabra
            - 0: Completamente irrazonable, imposible establecer cualquier asociación con la palabra
            - 0.2: Asociación extremadamente forzada
            - 0.4: Alguna asociación pero bastante forzada
            - 0.6: Asociación razonable pero no única
            - 0.8: Asociación altamente razonable
            - 1.0: Descripción que coincide completamente con las características de la palabra

            ## Formato de salida

            ```json
            {{
                "novelty": {{
                "score": Valor entre 0 y 1 (limitado a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explicación de por qué se dio esta puntuación"
                }},
                "relevance": {{
                "score": Valor entre 0 y 1 (limitado a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explicación de por qué se dio esta puntuación"
                }},
                "reasonableness": {{
                "score": Valor entre 0 y 1 (limitado a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explicación de por qué se dio esta puntuación"
                }}
            }}
            ```

            ## Ejemplos de referencia de puntuación

            ### Ejemplo 1: Balón de fútbol

            Supongamos que la palabra es "balón de fútbol", la declaración del jugador es "un objeto esférico", sin declaraciones previas de jugadores:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Esta es la primera declaración, por lo que es completamente novedosa"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "La descripción es muy amplia, aplicable a cualquier objeto esférico, no proporciona características únicas de un balón de fútbol"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "La descripción es completamente razonable, un balón de fútbol es efectivamente un objeto esférico"
                }}
            }}
            ```

            ### Ejemplo 2: Balón de fútbol

            Supongamos que la palabra es "balón de fútbol", la declaración del jugador es "uno de los deportes más populares del mundo, puede verse siendo pateado por personas en un campo verde", jugadores anteriores han dicho "un objeto esférico" y "un objeto blanco y negro":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "La descripción proporciona información completamente nueva, enfocándose en el balón de fútbol como atributo deportivo y escenario de uso, completamente diferente de las descripciones anteriores centradas en la apariencia"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "La descripción es altamente relevante, 'siendo pateado por personas en un campo verde' apunta directamente a un balón de fútbol, con casi ninguna otra posibilidad"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "La descripción está asociada de manera completamente razonable con un balón de fútbol, mencionando características fundamentales del fútbol"
                }}
            }}
            ```

            ### Ejemplo 3: Balón de fútbol

            Supongamos que la palabra es "balón de fútbol", la declaración del jugador es "me da dolor de cabeza", jugadores anteriores han dicho "una pelota que se puede patear" y "usado en un campo verde":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "La descripción proporciona una nueva perspectiva (relacionada con la sensación corporal), completamente diferente de las descripciones anteriores centradas en características físicas y escenarios de uso"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "La descripción proporciona algunas pistas (posiblemente aludiendo a los cabezazos), pero es muy vaga, muchas cosas podrían causar dolor de cabeza"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Aunque se podría conectar esto con cómo cabecear un balón de fútbol podría causar dolor de cabeza, esta asociación es bastante forzada y no es una característica típica o directa de los balones de fútbol"
                }}
            }}
            ```

            ### Ejemplo 4: Balón de fútbol

            Supongamos que la palabra es "balón de fútbol", la declaración del jugador actual es "una pelota que se patea sobre el césped", un jugador anterior ha dicho "una pelota usada en un campo verde":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "La descripción repite en gran medida el concepto previo de 'campo verde' (césped), añadiendo solo el detalle de la acción de 'patear'"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "La descripción es bastante específica, 'una pelota que se patea sobre el césped' apunta en gran medida a un balón de fútbol, pero también podría ser otros deportes de pelota"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "La descripción está asociada de manera completamente razonable con un balón de fútbol, coincidiendo con sus características básicas"
                }}
            }}
            ```





        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        Por favor, evalúa la declaración del siguiente jugador.
        # Información del jugador:
        Palabra del jugador: "{word1}"
        La otra palabra en este juego: "{word2}"
        Declaración del jugador: "{statement}"

        # Declaraciones históricas:
        {history}

        """
        return p
    



class player_prompt_de:

    
    def system_speak_player():
        p = f"""
            
            Du bist ein KI-Spieler, der am Spiel "Wer ist der Spion" teilnimmt. Du musst die Situation anhand der erhaltenen Informationen analysieren, deine Identität bestimmen und geeignete Sprechstrategien und -inhalte entwickeln.

            # Spielregeln

            1. Jeder Spieler erhält ein Wort. Die Mehrheit der Spieler erhält das gleiche Wort (Zivilisten), während eine Minderheit (1-2 Spieler) ein anderes, aber verwandtes Wort erhält (Spione).
            2. Das Spiel verläuft in Runden, wobei jeder Spieler sein Wort mit einem Satz beschreiben muss, ohne es direkt zu nennen.
            3. Nach jeder Beschreibungsrunde stimmen alle Spieler für denjenigen, den sie für den Spion halten. Der Spieler mit den meisten Stimmen scheidet aus.
            4. Wenn alle Spione ausgeschieden sind, gewinnen die Zivilisten; wenn die Anzahl der Spione die Anzahl der Zivilisten erreicht oder übersteigt, gewinnen die Spione.

            # Anforderungen an die Äußerungen

            1. Deine Aussage muss ein kurzer beschreibender Satz sein, keine lange Ausführung.
            2. Du kannst keine Aussagen wiederholen, die andere Spieler in früheren Runden gemacht haben.
            3. Deine Beschreibung kann breit oder spezifisch sein, muss aber zu dem Wort passen, das du erhalten hast. Du kannst keine Beschreibungen geben, die nicht zu deinem Wort passen.
            4. Bitte passe den Detaillierungsgrad deiner Beschreibung entsprechend deinen strategischen Bedürfnissen an. Unten sind Beispiele für verschiedene Detaillierungsgrade.

            # Beschreibungsbeispiele
            (Angenommen, das zu beschreibende Wort ist "Fußball")
            "Ein kugelförmiges Objekt" - Detaillierungsgrad 0.2 (zu breit, viele Objekte sind kugelförmig)
            "Ein Sportgerät" - Detaillierungsgrad 0.4 (spezifischer, aber deckt immer noch einen breiten Bereich ab)
            "Wird hauptsächlich mit dem Unterkörper der Athleten in Kontakt gebracht" - Detaillierungsgrad 0.6 (spezifischer, stärkere Richtungsangabe)
            "Wird üblicherweise mit einem Muster aus schwarzen und weißen Fünf- und Sechsecken dargestellt" - Detaillierungsgrad 0.8 (sehr spezifisch, fast nur Fußbälle sehen so aus)
            "Eine der beliebtesten Sportarten der Welt, man sieht, wie sie von Athleten auf einem grünen Feld getreten und geköpft wird" - Detaillierungsgrad 1.0 (zeigt eindeutig auf Fußball)



            # Deine Aufgabe

            1. Basierend auf dem gegebenen Wort und den Aussagen anderer Spieler, analysiere deine mögliche Identität (Zivilist oder Spion)
            2. Mit dem Ziel, dich selbst zu schützen und dein Spielziel zu erreichen, gib den Inhalt deiner Aussage an.
            3. Stelle deine Analyse und deinen Entscheidungsprozess im JSON-Format bereit

            # Ausgabeanforderungen

            Du musst im JSON-Format antworten und die folgenden Felder einschließen:
            {{
            "identity": "Analyse deiner eigenen Identität und der Identität anderer Spieler",
            "strategy": "Dein Denk- und Entscheidungsprozess",
            "statement": "Deine endgültige Aussage (du kannst deinen Analyseprozess nicht im Aussagefeld einschließen und du kannst dein Wort nicht direkt erwähnen)"
            }}

            # Strategietipps

            ### Zu Beginn des Spiels oder wenn die Identität noch unbestimmt ist: 

            Beginnen Sie mit sehr vagen, breiten Eigenschaften oder Merkmalen, und geben Sie dann detailliertere Beschreibungen des Wortes, nachdem Sie Ihre Identitätssituation allmählich bestimmt haben.

            ### Als Zivilist (du musst deine Zivilistenidentität selbst bestimmen):

            Analysiere die Aussagen anderer Spieler, um Beschreibungen zu finden, die nicht mit der Mehrheit übereinstimmen
            Verenge allmählich den Wortbereich, um dabei zu helfen, den Spion zu identifizieren
            Stelle sicher, dass deine Beschreibung zu deinem Wort passt, sage nichts, was nicht damit übereinstimmt


            ### Als Spion (du musst deine Spionidentität selbst bestimmen):

            Analysiere die Aussagen der Zivilisten sorgfältig, um ihr Wort zu erschließen
            Verwende vage Beschreibungen, die nicht sofort Verdacht erregen
            Stelle sicher, dass deine Beschreibung sowohl zu deinem Wort als auch zum Wort der Zivilisten passen kann (Zweideutigkeit)
            Vermeide Beschreibungen, die sich offensichtlich von denen anderer unterscheiden, aber folge ihnen auch nicht vollständig
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Hier sind Informationen zu dieser Spielrunde. Bitte analysiere diese Informationen, um deine Aufgabe zu erfüllen.
            # Deine persönlichen Informationen:
            Du bist player_{player_id}, dein Wort ist "{assigned_concept}".
            # Aussageverlauf für diese Spielrunde:
            {statement_history}
            # Deine Identitätsanalyse aus der vorherigen Runde:
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        Du bist ein KI-Spieler, der am Spiel "Wer ist der Spion" teilnimmt. Du musst die Situation anhand der erhaltenen Informationen analysieren, deine Identität bestimmen und entscheiden, für welchen Spieler du stimmen willst, um zu versuchen, ihn auszuschließen.

        # Spielregeln

        1. Jeder Spieler erhält ein Wort. Die Mehrheit der Spieler erhält das gleiche Wort (Zivilisten), während eine Minderheit (1-2 Spieler) ein anderes, aber verwandtes Wort erhält (Spione).
        2. Das Spiel verläuft in Runden, wobei jeder Spieler sein Wort mit einem Satz beschreiben muss, ohne es direkt zu nennen.
        3. Nach jeder Beschreibungsrunde stimmen alle Spieler für denjenigen, den sie für den Spion halten. Der Spieler mit den meisten Stimmen scheidet aus.
        4. Wenn alle Spione ausgeschieden sind, gewinnen die Zivilisten; wenn die Anzahl der Spione die Anzahl der Zivilisten erreicht oder übersteigt, gewinnen die Spione.

        # Deine Aufgabe

        1. Basierend auf dem gegebenen Wort und den Aussagen anderer Spieler, analysiere deine mögliche Identität (Zivilist oder Spion)
        2. Mit dem Ziel, dich selbst zu schützen und dein Spielziel zu erreichen, gib den Inhalt deiner Aussage an.
        3. Stelle deine Analyse und deinen Entscheidungsprozess im JSON-Format bereit

        # Ausgabeanforderungen

        Du musst im JSON-Format antworten und die folgenden Felder einschließen:
        {{
        "identity": "Analyse deiner Identität",
        "strategy": "Überlegungen zu deiner Strategie",
        "vote": "Der Spieler, für den du abstimmen möchtest (nur eine Nummer, keine zusätzliche Texterklärung erforderlich)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Hier sind Informationen zu dieser Spielrunde. Bitte analysiere diese Informationen, um deine Aufgabe zu erfüllen.
            # Deine persönlichen Informationen:
            Du bist player_{player_id}, dein Wort ist "{assigned_concept}".
            # Der Beschreibungsverlauf für diese Spielrunde ist:
            {statement_history}
            # Deine Identitätsanalyse aus der vorherigen Runde:
            {last_analyze}
            # Die Liste der aktuell überlebenden Spieler ist:
            {alive_players}
            Du kannst nur eine Nummer aus diesen als deine Stimme wählen.
        """
        return p 












class judge_prompt_de:


    def system_judge():
        p = f"""
            
            # Schiedsrichter-Leitfaden für das Spiel "Wer ist der Spion"

            Du bist der Schiedsrichter für das Spiel "Wer ist der Spion", verantwortlich für die Analyse der Aussage jedes Spielers und deren Bewertung nach den folgenden Kriterien. Du musst deine Bewertungsergebnisse im JSON-Format ausgeben.

            ## Bewertungsdimensionen

            1. **Neuheit**：Ob die aktuelle Aussage Inhalte aus früheren Spieleraussagen wiederholt
            - 0: Wiederholt vollständig die Beschreibung eines früheren Spielers
            - 0.2: Größtenteils wiederholend, mit nur minimalen neuen Informationen
            - 0.4: Wiederholt teilweise frühere Inhalte, mit einigen zusätzlichen Inhalten
            - 0.6: Hauptsächlich neuer Inhalt, aber mit einigen Wiederholungen
            - 0.8: Fast vollständig neuer Inhalt, mit einer anderen Perspektive als frühere Beschreibungen
            - 1.0: Vollständig neue Beschreibung, die eine völlig neue Perspektive oder Information bietet

            2. **Relevanz**：Der Grad der Relevanz und Spezifität zwischen der Aussage und den Merkmalen des Wortes
            - 0: Völlig irrelevant
            - 0.2: Extrem breite Beschreibung, anwendbar auf eine große Anzahl von Objekten/Konzepten
            - 0.4: Breite, aber etwas gerichtete Beschreibung
            - 0.6: Klare Hinweise, könnte aber immer noch auf mehrere ähnliche Dinge hinweisen
            - 0.8: Hochspezifische Beschreibung, die im Wesentlichen nur auf das Zielwort oder sehr wenige ähnliche Objekte hinweist
            - 1.0: Beschreibung, die fast direkt auf das Wort hinweist

            3. **Angemessenheit**：Wie angemessen die Verbindung zwischen der Beschreibung und dem Wort ist
            - 0: Völlig unangemessen, unmöglich, irgendeine Verbindung mit dem Wort herzustellen
            - 0.2: Extrem weit hergeholte Verbindung
            - 0.4: Einige Verbindung, aber ziemlich weit hergeholt
            - 0.6: Angemessene, aber nicht einzigartige Verbindung
            - 0.8: Hochgradig angemessene Verbindung
            - 1.0: Beschreibung, die vollständig mit den Merkmalen des Wortes übereinstimmt

            ## Ausgabeformat

            ```json
            {{
                "novelty": {{
                "score": Wert zwischen 0 und 1 (begrenzt auf 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Erklärung, warum diese Punktzahl vergeben wurde"
                }},
                "relevance": {{
                "score": Wert zwischen 0 und 1 (begrenzt auf 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Erklärung, warum diese Punktzahl vergeben wurde"
                }},
                "reasonableness": {{
                "score": Wert zwischen 0 und 1 (begrenzt auf 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Erklärung, warum diese Punktzahl vergeben wurde"
                }}
            }}
            ```

            ## Bewertungsreferenzbeispiele

            ### Beispiel 1: Fußball

            Angenommen, das Wort ist "Fußball", die Aussage des Spielers ist "ein kugelförmiges Objekt", ohne vorherige Spieleraussagen:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Dies ist die erste Aussage, daher ist sie völlig neu"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "Die Beschreibung ist sehr breit, anwendbar auf jedes kugelförmige Objekt, bietet keine für einen Fußball einzigartigen Merkmale"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "Die Beschreibung ist völlig angemessen, ein Fußball ist tatsächlich ein kugelförmiges Objekt"
                }}
            }}
            ```

            ### Beispiel 2: Fußball

            Angenommen, das Wort ist "Fußball", die Aussage des Spielers ist "eine der beliebtesten Sportarten der Welt, man kann sehen, wie er von Menschen auf einem grünen Feld getreten wird", frühere Spieler haben "ein kugelförmiges Objekt" und "ein schwarz-weißes Objekt" gesagt:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Die Beschreibung liefert völlig neue Informationen, konzentriert sich auf den Fußball als Sportattribut und Nutzungsszenario, völlig anders als frühere Beschreibungen, die sich auf das Aussehen konzentrierten"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "Die Beschreibung ist hochgradig relevant, 'von Menschen auf einem grünen Feld getreten werden' weist direkt auf einen Fußball hin, mit fast keinen anderen Möglichkeiten"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "Die Beschreibung ist vollständig angemessen mit einem Fußball verbunden und erwähnt Kernmerkmale des Fußballs"
                }}
            }}
            ```

            ### Beispiel 3: Fußball

            Angenommen, das Wort ist "Fußball", die Aussage des Spielers ist "er verursacht mir Kopfschmerzen", frühere Spieler haben "ein Ball, den man treten kann" und "wird auf einem grünen Feld verwendet" gesagt:

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "Die Beschreibung bietet eine neue Perspektive (bezogen auf körperliche Empfindung), völlig anders als frühere Beschreibungen, die sich auf physische Eigenschaften und Nutzungsszenarien konzentrierten"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "Die Beschreibung bietet einige Hinweise (möglicherweise Anspielung auf Kopfbälle), ist aber sehr vage, viele Dinge könnten Kopfschmerzen verursachen"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Obwohl man dies damit verbinden könnte, wie Kopfbälle beim Fußball zu Kopfschmerzen führen könnten, ist diese Verbindung ziemlich weit hergeholt und kein typisches oder direktes Merkmal von Fußbällen"
                }}
            }}
            ```

            ### Beispiel 4: Fußball

            Angenommen, das Wort ist "Fußball", die aktuelle Spieleraussage ist "ein Ball, der auf Gras getreten wird", ein früherer Spieler hat "ein Ball, der auf einem grünen Feld verwendet wird" gesagt:

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "Die Beschreibung wiederholt größtenteils das vorherige Konzept 'grünes Feld' (Gras) und fügt nur das Detail der 'Tret'-Aktion hinzu"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "Die Beschreibung ist ziemlich spezifisch, 'ein Ball, der auf Gras getreten wird' weist weitgehend auf einen Fußball hin, könnte aber auch andere Ballsportarten sein"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "Die Beschreibung ist vollständig angemessen mit einem Fußball verbunden und stimmt mit seinen grundlegenden Merkmalen überein"
                }}
            }}
            ```





        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        Bitte bewerte die Aussage des folgenden Spielers.
        # Spielerinformationen:
        Wort des Spielers: "{word1}"
        Das andere Wort in diesem Spiel: "{word2}"
        Aussage des Spielers: "{statement}"

        # Historische Aussagen:
        {history}

        """
        return p
    

class player_prompt_it:

    
    def system_speak_player():
        p = f"""
            
            Sei un giocatore IA che partecipa al gioco "Chi è la spia". Devi analizzare la situazione in base alle informazioni ricevute, determinare la tua identità e sviluppare appropriate strategie e contenuti di dichiarazione.

            # Regole del gioco

            1. Ogni giocatore riceve una parola. La maggioranza dei giocatori riceve la stessa parola (civili), mentre una minoranza (1-2 giocatori) riceve una parola diversa ma correlata (spie).
            2. Il gioco procede a turni, con ogni giocatore che deve descrivere la propria parola con una frase, senza dirla direttamente.
            3. Dopo ogni round di descrizioni, tutti i giocatori votano per chi pensano sia la spia. Il giocatore con più voti viene eliminato.
            4. Se tutte le spie vengono eliminate, i civili vincono; se il numero di spie è uguale o superiore al numero dei civili, le spie vincono.

            # Requisiti per le dichiarazioni

            1. La tua dichiarazione deve essere una breve frase descrittiva, non una lunga esposizione.
            2. Non puoi ripetere dichiarazioni fatte da altri giocatori nei turni precedenti.
            3. La tua descrizione può essere ampia o specifica, ma deve corrispondere alla parola che hai ricevuto. Non puoi fornire descrizioni che non corrispondono alla tua parola.
            4. Regola il livello di dettaglio nella tua descrizione in base alle tue esigenze strategiche. Di seguito sono riportati esempi di diversi livelli di dettaglio.

            # Esempi di descrizione
            (Supponendo che la parola da descrivere sia "pallone da calcio")
            "Un oggetto sferico" - Livello di dettaglio 0.2 (troppo generico, molti oggetti sono sferici)
            "Un'attrezzatura sportiva" - Livello di dettaglio 0.4 (più specifico, ma copre ancora un'ampia gamma)
            "Principalmente a contatto con la parte inferiore del corpo degli atleti" - Livello di dettaglio 0.6 (più specifico, indicazione direzionale più forte)
            "Comunemente raffigurato con un motivo di pentagoni e esagoni bianchi e neri" - Livello di dettaglio 0.8 (molto specifico, quasi solo i palloni da calcio appaiono così)
            "Uno degli sport più popolari al mondo, si vede calciato e colpito di testa dagli atleti su un campo verde" - Livello di dettaglio 1.0 (punta completamente al pallone da calcio)



            # Il tuo compito

            1. In base alla parola data e alle dichiarazioni degli altri giocatori, analizza la tua possibile identità (civile o spia)
            2. Con l'obiettivo di proteggere te stesso e raggiungere il tuo obiettivo di gioco, fornisci il contenuto della tua dichiarazione.
            3. Fornisci la tua analisi e il processo decisionale in formato JSON

            # Requisiti di output

            Devi rispondere in formato JSON, includendo i seguenti campi:
            {{
            "identity": "Analisi della tua identità e dell'identità degli altri giocatori",
            "strategy": "Il tuo processo di pensiero e decisionale",
            "statement": "La tua dichiarazione finale (non puoi includere il tuo processo di analisi nel campo statement, e non puoi menzionare direttamente la tua parola)"
            }}

            # Suggerimenti strategici

            ### All'inizio del gioco o quando l'identità è ancora indeterminata: 

            inizia con caratteristiche o proprietà molto vaghe e generali, poi fornisci descrizioni più dettagliate della parola dopo aver gradualmente determinato la tua situazione di identità.

            ### Come civile (devi determinare da solo la tua identità civile):

            Analizza le dichiarazioni degli altri giocatori per trovare descrizioni inconsistenti con la maggioranza
            Riduci gradualmente la gamma di parole per aiutare a identificare la spia
            Assicurati che la tua descrizione corrisponda alla tua parola, non dire nulla di inconsistente con essa


            ### Come spia (devi determinare da solo la tua identità di spia):

            Analizza attentamente le dichiarazioni dei civili per dedurre la loro parola
            Usa descrizioni vaghe che non susciteranno immediatamente sospetti
            Assicurati che la tua descrizione possa corrispondere sia alla tua parola che alla parola dei civili (ambiguità)
            Evita descrizioni palesemente diverse dagli altri, ma non seguirle completamente
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Qui ci sono informazioni relative a questo round di gioco. Analizza queste informazioni per completare il tuo compito.
            # Le tue informazioni personali:
            Sei player_{player_id}, la tua parola è "{assigned_concept}".
            # Cronologia delle dichiarazioni per questo round di gioco:
            {statement_history}
            # La tua analisi dell'identità dal round precedente:
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        Sei un giocatore IA che partecipa al gioco "Chi è la spia". Devi analizzare la situazione in base alle informazioni ricevute, determinare la tua identità e decidere di votare per un giocatore per cercare di eliminarlo.

        # Regole del gioco

        1. Ogni giocatore riceve una parola. La maggioranza dei giocatori riceve la stessa parola (civili), mentre una minoranza (1-2 giocatori) riceve una parola diversa ma correlata (spie).
        2. Il gioco procede a turni, con ogni giocatore che deve descrivere la propria parola con una frase, senza dirla direttamente.
        3. Dopo ogni round di descrizioni, tutti i giocatori votano per chi pensano sia la spia. Il giocatore con più voti viene eliminato.
        4. Se tutte le spie vengono eliminate, i civili vincono; se il numero di spie è uguale o superiore al numero dei civili, le spie vincono.

        # Il tuo compito

        1. In base alla parola data e alle dichiarazioni degli altri giocatori, analizza la tua possibile identità (civile o spia)
        2. Con l'obiettivo di proteggere te stesso e raggiungere il tuo obiettivo di gioco, fornisci il contenuto della tua dichiarazione.
        3. Fornisci la tua analisi e il processo decisionale in formato JSON

        # Requisiti di output

        Devi rispondere in formato JSON, includendo i seguenti campi:
        {{
        "identity": "Analisi della tua identità",
        "strategy": "Pensiero sulla tua strategia",
        "vote": "Il giocatore per cui vuoi votare (solo un numero, senza necessità di spiegazioni testuali aggiuntive)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Qui ci sono informazioni relative a questo round di gioco. Analizza queste informazioni per completare il tuo compito.
            # Le tue informazioni personali:
            Sei player_{player_id}, la tua parola è "{assigned_concept}".
            # La cronologia delle descrizioni per questo round di gioco è:
            {statement_history}
            # La tua analisi dell'identità dal round precedente:
            {last_analyze}
            # L'elenco dei giocatori attualmente sopravvissuti è:
            {alive_players}
            Puoi scegliere solo un numero da questi come tuo voto.
        """
        return p 












class judge_prompt_it:


    def system_judge():
        p = f"""
            
            # Guida dell'Arbitro del Gioco "Chi è la Spia"

            Sei l'arbitro del gioco "Chi è la spia", responsabile dell'analisi della dichiarazione di ciascun giocatore e della sua valutazione secondo i seguenti criteri. Devi fornire i risultati della tua valutazione in formato JSON.

            ## Dimensioni di valutazione

            1. **Novità**：Se la dichiarazione attuale ripete contenuti dalle dichiarazioni dei giocatori precedenti
            - 0: Ripete completamente la descrizione di un giocatore precedente
            - 0.2: Prevalentemente ripetitivo, con solo informazioni nuove minime
            - 0.4: Ripete parzialmente contenuti precedenti, con alcuni contenuti aggiuntivi
            - 0.6: Principalmente contenuti nuovi, ma con alcune ripetizioni
            - 0.8: Contenuti quasi interamente nuovi, con una prospettiva diversa dalle descrizioni precedenti
            - 1.0: Descrizione completamente nuova, che fornisce una prospettiva o informazioni del tutto nuove

            2. **Rilevanza**：Il grado di rilevanza e specificità tra la dichiarazione e le caratteristiche della parola
            - 0: Completamente irrilevante
            - 0.2: Descrizione estremamente ampia, applicabile a un gran numero di oggetti/concetti
            - 0.4: Descrizione ampia ma con una certa direzionalità
            - 0.6: Indizi chiari, ma potrebbero ancora indicare molteplici cose simili
            - 0.8: Descrizione altamente specifica, che indica fondamentalmente solo la parola target o pochissimi oggetti simili
            - 1.0: Descrizione che indica quasi direttamente la parola

            3. **Ragionevolezza**：Quanto è ragionevole l'associazione tra la descrizione e la parola
            - 0: Completamente irragionevole, impossibile stabilire qualsiasi associazione con la parola
            - 0.2: Associazione estremamente forzata
            - 0.4: Qualche associazione ma piuttosto forzata
            - 0.6: Associazione ragionevole ma non unica
            - 0.8: Associazione altamente ragionevole
            - 1.0: Descrizione che corrisponde completamente alle caratteristiche della parola

            ## Formato di output

            ```json
            {{
                "novelty": {{
                "score": Valore tra 0 e 1 (limitato a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Spiegazione del motivo per cui è stato assegnato questo punteggio"
                }},
                "relevance": {{
                "score": Valore tra 0 e 1 (limitato a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Spiegazione del motivo per cui è stato assegnato questo punteggio"
                }},
                "reasonableness": {{
                "score": Valore tra 0 e 1 (limitato a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Spiegazione del motivo per cui è stato assegnato questo punteggio"
                }}
            }}
            ```

            ## Esempi di riferimento per il punteggio

            ### Esempio 1: Pallone da calcio

            Supponiamo che la parola sia "pallone da calcio", la dichiarazione del giocatore è "un oggetto sferico", senza dichiarazioni precedenti dei giocatori:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Questa è la prima dichiarazione, quindi è completamente nuova"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "La descrizione è molto ampia, applicabile a qualsiasi oggetto sferico, non fornisce caratteristiche uniche di un pallone da calcio"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "La descrizione è completamente ragionevole, un pallone da calcio è effettivamente un oggetto sferico"
                }}
            }}
            ```

            ### Esempio 2: Pallone da calcio

            Supponiamo che la parola sia "pallone da calcio", la dichiarazione del giocatore è "uno degli sport più popolari al mondo, si può vedere calciato dalle persone su un campo verde", i giocatori precedenti hanno detto "un oggetto sferico" e "un oggetto bianco e nero":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "La descrizione fornisce informazioni completamente nuove, concentrandosi sul pallone da calcio come attributo sportivo e scenario d'uso, completamente diverso dalle descrizioni precedenti incentrate sull'aspetto"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "La descrizione è altamente rilevante, 'calciato dalle persone su un campo verde' indica direttamente un pallone da calcio, con quasi nessun'altra possibilità"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "La descrizione è associata in modo completamente ragionevole a un pallone da calcio, menzionando caratteristiche fondamentali del calcio"
                }}
            }}
            ```

            ### Esempio 3: Pallone da calcio

            Supponiamo che la parola sia "pallone da calcio", la dichiarazione del giocatore è "mi dà mal di testa", i giocatori precedenti hanno detto "una palla che si può calciare" e "usato su un campo verde":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "La descrizione fornisce una nuova prospettiva (legata alla sensazione corporea), completamente diversa dalle descrizioni precedenti incentrate su caratteristiche fisiche e scenari d'uso"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "La descrizione fornisce alcuni indizi (forse alludendo ai colpi di testa), ma è molto vaga, molte cose potrebbero causare mal di testa"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Sebbene si possa collegare questo a come i colpi di testa con un pallone da calcio potrebbero causare mal di testa, questa associazione è piuttosto forzata e non è una caratteristica tipica o diretta dei palloni da calcio"
                }}
            }}
            ```

            ### Esempio 4: Pallone da calcio

            Supponiamo che la parola sia "pallone da calcio", la dichiarazione del giocatore attuale è "una palla che viene calciata sull'erba", un giocatore precedente ha detto "una palla usata su un campo verde":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "La descrizione ripete in gran parte il concetto precedente di 'campo verde' (erba), aggiungendo solo il dettaglio dell'azione di 'calciare'"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "La descrizione è abbastanza specifica, 'una palla che viene calciata sull'erba' indica in gran parte un pallone da calcio, ma potrebbe essere anche altri sport con la palla"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "La descrizione è associata in modo completamente ragionevole a un pallone da calcio, corrispondendo alle sue caratteristiche di base"
                }}
            }}
            ```





        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        Per favore, valuta la dichiarazione del seguente giocatore.
        # Informazioni sul giocatore:
        Parola del giocatore: "{word1}"
        L'altra parola in questo gioco: "{word2}"
        Dichiarazione del giocatore: "{statement}"

        # Dichiarazioni storiche:
        {history}

        """
        return p
    



class player_prompt_pt:

    
    def system_speak_player():
        p = f"""
            
            Você é um jogador de IA participando do jogo "Quem é o espião". Você precisa analisar a situação com base nas informações recebidas, determinar sua identidade e elaborar estratégias e conteúdos de fala apropriados.

            # Regras do jogo

            1. Cada jogador recebe uma palavra. A maioria dos jogadores recebe a mesma palavra (civis), enquanto uma minoria (1-2 jogadores) recebe uma palavra diferente, mas relacionada (espiões).
            2. O jogo prossegue em turnos, com cada jogador usando uma frase para descrever sua palavra sem dizê-la diretamente.
            3. Após cada rodada de descrições, todos os jogadores votam em quem acreditam ser o espião. O jogador com mais votos é eliminado.
            4. Se todos os espiões forem eliminados, os civis vencem; se o número de espiões igualar ou superar o número de civis, os espiões vencem.

            # Requisitos para falar

            1. Sua declaração deve ser uma breve frase descritiva, não uma exposição longa.
            2. Você não pode repetir declarações feitas por outros jogadores em rodadas anteriores.
            3. Sua descrição pode ser ampla ou específica, mas deve corresponder à palavra que você recebeu. Você não pode dar descrições que não correspondam à sua palavra.
            4. Por favor, ajuste o nível de detalhe em sua descrição de acordo com suas necessidades estratégicas. Abaixo estão exemplos de diferentes níveis de detalhe.

            # Exemplos de descrição
            (Supondo que a palavra a ser descrita seja "bola de futebol")
            "Um objeto esférico" - Nível de detalhe 0.2 (muito amplo, muitos objetos são esféricos)
            "Um equipamento esportivo" - Nível de detalhe 0.4 (mais específico, mas ainda cobre uma ampla gama)
            "Principalmente contatado pela parte inferior do corpo dos atletas" - Nível de detalhe 0.6 (mais específico, indicação direcional mais forte)
            "Comumente representado com um padrão de pentágonos e hexágonos pretos e brancos" - Nível de detalhe 0.8 (muito específico, quase só bolas de futebol parecem assim)
            "Um dos esportes mais populares do mundo, pode-se ver sendo chutado e cabeceado por atletas em um campo verde" - Nível de detalhe 1.0 (aponta completamente para a bola de futebol)



            # Sua tarefa

            1. Com base na palavra dada e nas declarações de outros jogadores, analise sua possível identidade (civil ou espião)
            2. Com o objetivo de proteger a si mesmo e cumprir seu objetivo no jogo, forneça o conteúdo da sua declaração.
            3. Forneça sua análise e processo de tomada de decisão em formato JSON

            # Requisitos de saída

            Você deve responder em formato JSON, incluindo os seguintes campos:
            {{
            "identity": "Análise da sua própria identidade e da identidade de outros jogadores",
            "strategy": "Seu processo de pensamento e tomada de decisão",
            "statement": "Sua declaração final (você não pode incluir seu processo de análise no campo statement, e não pode mencionar diretamente sua palavra)"
            }}

            # Dicas de estratégia

            ### No início do jogo ou quando a identidade ainda está indeterminada: 

            comece com características ou propriedades muito vagas e amplas, e depois forneça descrições mais detalhadas da palavra após determinar gradualmente sua situação de identidade.

            ### Como civil (você precisa determinar sua identidade civil por conta própria):

            Analise as declarações de outros jogadores para encontrar descrições inconsistentes com a maioria
            Reduza gradualmente a gama de palavras para ajudar a identificar o espião
            Certifique-se de que sua descrição corresponda à sua palavra, não diga nada inconsistente com ela


            ### Como espião (você precisa determinar sua identidade de espião por conta própria):

            Analise cuidadosamente as declarações dos civis para inferir a palavra deles
            Use descrições vagas que não despertarão suspeitas imediatas
            Certifique-se de que sua descrição possa corresponder tanto à sua palavra quanto à palavra dos civis (ambiguidade)
            Evite descrições obviamente diferentes das dos outros, mas também não as siga completamente
        
        """
        return p 
    


    def user_speak_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Aqui estão informações relacionadas a esta rodada de jogo. Por favor, analise essas informações para completar sua tarefa.
            # Suas informações pessoais:
            Você é player_{player_id}, sua palavra é "{assigned_concept}".
            # Histórico de declarações para esta rodada de jogo:
            {statement_history}
            # Sua análise de identidade da rodada anterior:
            {last_analyze}
        """
        return p 
    

    def system_vote_player():
        p = f"""
        Você é um jogador de IA participando do jogo "Quem é o espião". Você precisa analisar a situação com base nas informações recebidas, determinar sua identidade e decidir votar em um jogador para tentar eliminá-lo.

        # Regras do jogo

        1. Cada jogador recebe uma palavra. A maioria dos jogadores recebe a mesma palavra (civis), enquanto uma minoria (1-2 jogadores) recebe uma palavra diferente, mas relacionada (espiões).
        2. O jogo prossegue em turnos, com cada jogador usando uma frase para descrever sua palavra sem dizê-la diretamente.
        3. Após cada rodada de descrições, todos os jogadores votam em quem acreditam ser o espião. O jogador com mais votos é eliminado.
        4. Se todos os espiões forem eliminados, os civis vencem; se o número de espiões igualar ou superar o número de civis, os espiões vencem.

        # Sua tarefa

        1. Com base na palavra dada e nas declarações de outros jogadores, analise sua possível identidade (civil ou espião)
        2. Com o objetivo de proteger a si mesmo e cumprir seu objetivo no jogo, forneça o conteúdo da sua declaração.
        3. Forneça sua análise e processo de tomada de decisão em formato JSON

        # Requisitos de saída

        Você deve responder em formato JSON, incluindo os seguintes campos:
        {{
        "identity": "Análise da sua identidade",
        "strategy": "Pensando sobre sua estratégia",
        "vote": "O jogador em quem você quer votar (apenas um número, sem necessidade de explicação textual adicional)"
        }}
        """
        return p 
    

    def user_vote_player(player_id, assigned_concept, statement_history, last_analyze, alive_players):
        p = f"""
        Aqui estão informações relacionadas a esta rodada de jogo. Por favor, analise essas informações para completar sua tarefa.
            # Suas informações pessoais:
            Você é player_{player_id}, sua palavra é "{assigned_concept}".
            # O histórico de descrições para esta rodada de jogo é:
            {statement_history}
            # Sua análise de identidade da rodada anterior:
            {last_analyze}
            # A lista de jogadores atualmente sobreviventes é:
            {alive_players}
            Você só pode escolher um número destes como seu voto.
        """
        return p 












class judge_prompt_pt:


    def system_judge():
        p = f"""
            
            # Guia do Árbitro do Jogo "Quem é o Espião"

            Você é o árbitro do jogo "Quem é o espião", responsável por analisar a declaração de cada jogador e pontuá-la de acordo com os seguintes critérios. Você precisa apresentar seus resultados de avaliação em formato JSON.

            ## Dimensões de avaliação

            1. **Novidade**：Se a declaração atual repete conteúdo das declarações de jogadores anteriores
            - 0: Repete completamente a descrição de um jogador anterior
            - 0.2: Majoritariamente repetitivo, com apenas informações novas mínimas
            - 0.4: Repete parcialmente o conteúdo anterior, com algum conteúdo adicional
            - 0.6: Principalmente conteúdo novo, mas com alguma repetição
            - 0.8: Conteúdo quase inteiramente novo, com uma perspectiva diferente das descrições anteriores
            - 1.0: Descrição completamente nova, fornecendo uma perspectiva ou informação inteiramente nova

            2. **Relevância**：O grau de relevância e especificidade entre a declaração e as características da palavra
            - 0: Completamente irrelevante
            - 0.2: Descrição extremamente ampla, aplicável a um grande número de objetos/conceitos
            - 0.4: Descrição ampla, mas com alguma direcionalidade
            - 0.6: Pistas claras, mas ainda poderia apontar para múltiplas coisas similares
            - 0.8: Descrição altamente específica, basicamente apontando apenas para a palavra-alvo ou muito poucos objetos similares
            - 1.0: Descrição que quase aponta diretamente para a palavra

            3. **Razoabilidade**：Quão razoável é a associação entre a descrição e a palavra
            - 0: Completamente irrazoável, impossível estabelecer qualquer associação com a palavra
            - 0.2: Associação extremamente forçada
            - 0.4: Alguma associação, mas bastante forçada
            - 0.6: Associação razoável, mas não única
            - 0.8: Associação altamente razoável
            - 1.0: Descrição que corresponde completamente às características da palavra

            ## Formato de saída

            ```json
            {{
                "novelty": {{
                "score": Valor entre 0 e 1 (limitado a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explicação de por que essa pontuação foi dada"
                }},
                "relevance": {{
                "score": Valor entre 0 e 1 (limitado a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explicação de por que essa pontuação foi dada"
                }},
                "reasonableness": {{
                "score": Valor entre 0 e 1 (limitado a 0, 0.2, 0.4, 0.6, 0.8, 1),
                "explanation": "Explicação de por que essa pontuação foi dada"
                }}
            }}
            ```

            ## Exemplos de referência de pontuação

            ### Exemplo 1: Bola de futebol

            Suponha que a palavra seja "bola de futebol", a declaração do jogador é "um objeto esférico", sem declarações prévias de jogadores:

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "Esta é a primeira declaração, então é completamente nova"
                }},
                "relevance": {{
                "score": 0.2,
                "explanation": "A descrição é muito ampla, aplicável a qualquer objeto esférico, não fornece características únicas de uma bola de futebol"
                }},
                "reasonableness": {{
                "score": 1,
                "explanation": "A descrição é completamente razoável, uma bola de futebol é de fato um objeto esférico"
                }}
            }}
            ```

            ### Exemplo 2: Bola de futebol

            Suponha que a palavra seja "bola de futebol", a declaração do jogador é "um dos esportes mais populares do mundo, pode-se ver sendo chutado por pessoas em um campo verde", jogadores anteriores disseram "um objeto esférico" e "um objeto preto e branco":

            ```json
            {{
                "novelty": {{
                "score": 1.0,
                "explanation": "A descrição fornece informações completamente novas, focando na bola de futebol como atributo esportivo e cenário de uso, completamente diferente das descrições anteriores focadas na aparência"
                }},
                "relevance": {{
                "score": 1.0,
                "explanation": "A descrição é altamente relevante, 'sendo chutado por pessoas em um campo verde' aponta diretamente para uma bola de futebol, com quase nenhuma outra possibilidade"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "A descrição está completamente e razoavelmente associada a uma bola de futebol, mencionando características fundamentais do futebol"
                }}
            }}
            ```

            ### Exemplo 3: Bola de futebol

            Suponha que a palavra seja "bola de futebol", a declaração do jogador é "me dá dor de cabeça", jogadores anteriores disseram "uma bola que pode ser chutada" e "usada em um campo verde":

            ```json
            {{
                "novelty": {{
                "score": 0.8,
                "explanation": "A descrição fornece uma nova perspectiva (relacionada à sensação corporal), completamente diferente das descrições anteriores focadas em características físicas e cenários de uso"
                }},
                "relevance": {{
                "score": 0.4,
                "explanation": "A descrição fornece algumas pistas (possivelmente aludindo a cabeçadas), mas é muito vaga, muitas coisas poderiam causar dor de cabeça"
                }},
                "reasonableness": {{
                "score": 0.2,
                "explanation": "Embora possa ser conectado a como cabecear uma bola de futebol poderia causar dor de cabeça, essa associação é bastante forçada e não é uma característica típica ou direta de bolas de futebol"
                }}
            }}
            ```

            ### Exemplo 4: Bola de futebol

            Suponha que a palavra seja "bola de futebol", a declaração atual do jogador é "uma bola que é chutada na grama", um jogador anterior disse "uma bola usada em um campo verde":

            ```json
            {{
                "novelty": {{
                "score": 0.4,
                "explanation": "A descrição repete em grande parte o conceito anterior de 'campo verde' (grama), adicionando apenas o detalhe da ação de 'chutar'"
                }},
                "relevance": {{
                "score": 0.8,
                "explanation": "A descrição é bastante específica, 'uma bola que é chutada na grama' aponta em grande parte para uma bola de futebol, mas poderia ser também outros esportes com bola"
                }},
                "reasonableness": {{
                "score": 1.0,
                "explanation": "A descrição está completamente e razoavelmente associada a uma bola de futebol, correspondendo às suas características básicas"
                }}
            }}
            ```





        """
        
        return p



    def user_judge(word1, word2, statement, history):
        p = f"""
        Por favor, avalie a declaração do seguinte jogador.
        # Informações do jogador:
        Palavra do jogador: "{word1}"
        A outra palavra neste jogo: "{word2}"
        Declaração do jogador: "{statement}"

        # Declarações históricas:
        {history}

        """
        return p