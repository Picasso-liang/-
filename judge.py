import random
from collections import defaultdict
all_tags = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42']
def get_next_questions(error_tags_str, all_tags, question_tag_list, count=10, 
                      base_weight=0.3, decay_factor=0.85, diversity_factor=0.2):
    """
    根据错题标签权重计算题目权重并返回多个题目ID
    
    参数:
    error_tags_str: 包含错题标签ID的字符串，以星号(*)分隔
    all_tags: 包含所有标签ID的列表
    question_tag_list: 包含题目与标签对应关系的列表，格式为[(题目ID, 标签ID), ...]
    count: 需要返回的题目数量 (默认10)
    base_weight: 基础权重值
    decay_factor: 遗忘衰减因子
    diversity_factor: 多样性因子 (0-1)，增加低权重题目的选择机会
    
    返回:
    按权重随机选择的题目ID列表 (长度为count)
    """
    # 1. 解析错题标签字符串
    error_tags = error_tags_str.split('*') if error_tags_str else []
    
    # 2. 初始化标签权重（所有标签初始权重为0）
    tag_weights = {tag: 0.0 for tag in all_tags}
    
    # 3. 更新错题标签权重
    for tag in error_tags:
        if tag in tag_weights:
            tag_weights[tag] += 1.0
    
    # 4. 应用遗忘衰减因子
    for tag in tag_weights:
        tag_weights[tag] *= decay_factor
    
    # 5. 构建题目到标签的映射
    question_tags = defaultdict(list)
    for qid, tag in question_tag_list:
        question_tags[qid].append(tag)
    
    # 6. 计算题目权重
    question_weights = {}
    for qid, tags in question_tags.items():
        # 题目权重 = 基础权重 + 相关标签权重之和
        total_tag_weight = sum(tag_weights.get(tag, 0) for tag in tags)
        question_weights[qid] = base_weight + total_tag_weight
    
    # 7. 添加多样性因子，确保低权重题目也有机会被选中
    min_weight = min(question_weights.values()) if question_weights else 0
    max_weight = max(question_weights.values()) if question_weights else 1
    
    for qid in question_weights:
        # 标准化权重 (0-1范围)
        normalized_weight = (question_weights[qid] - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
        
        # 应用多样性因子
        diversity_adjust = diversity_factor * (1 - normalized_weight)
        question_weights[qid] += diversity_adjust
    
    # 8. 准备加权随机选择
    questions = list(question_weights.keys())
    weights = list(question_weights.values())
    
    # 如果题目数量不足，直接返回所有题目
    if len(questions) <= count:
        return questions
    
    # 9. 加权随机选择多个题目（不重复）
    selected_questions = []
    
    # 方法1: 使用random.choices + 去重（可能多次选择同一题目）
    # 改为方法2: 使用加权抽样后去重，直到获得足够数量
    while len(selected_questions) < count:
        # 计算剩余需要选择的题目数量
        remaining = count - len(selected_questions)
        
        # 创建去重后的候选列表
        candidate_questions = [q for q in questions if q not in selected_questions]
        candidate_weights = [weights[questions.index(q)] for q in candidate_questions]
        
        # 如果候选题目不足，直接返回已选题目
        if len(candidate_questions) == 0:
            break
        
        # 计算总权重
        total_weight = sum(candidate_weights)
        
        # 如果所有权重为0，则平均分配权重
        if total_weight <= 0:
            candidate_weights = [1.0] * len(candidate_questions)
            total_weight = len(candidate_questions)
        
        # 计算概率
        probabilities = [w / total_weight for w in candidate_weights]
        
        # 选择题目（尽可能一次选择多个，提高效率）
        select_count = min(remaining, len(candidate_questions))
        new_selections = random.choices(candidate_questions, weights=probabilities, k=select_count)
        
        # 添加到结果（去重）
        for q in new_selections:
            if q not in selected_questions:
                selected_questions.append(q)
    return selected_questions

# 使用示例
if __name__ == "__main__":
    # 示例数据
    error_tags_str = "2*3*5"  # 错题标签ID，以星号分隔
    all_tags = ["1", "2", "3", "4", "5"]  # 所有标签ID
    question_tag_list = [
        ("11", "2"), ("11", "3"),  # 题目11对应标签2和3
        ("12", "3"), ("12", "4"),  # 题目12对应标签3和4
        ("13", "1"), ("13", "5"),  # 题目13对应标签1和5
        ("14", "4"),               # 题目14对应标签4
        ("15", "5"), ("15", "1"),  # 题目15对应标签5和1
        ("16", "2"), ("16", "5"),  # 题目16对应标签2和5
        ("17", "1"), ("17", "3"),  # 题目17对应标签1和3
        ("18", "4"), ("18", "5"),  # 题目18对应标签4和5
        ("19", "2"),               # 题目19对应标签2
        ("20", "3")                # 题目20对应标签3
    ]
    
    # 获取10个题目
    next_questions = get_next_questions(error_tags_str, all_tags, question_tag_list, count=10)
    print(next_questions)
    print("推荐的10个题目ID:")
    for i, qid in enumerate(next_questions, 1):
        print(f"{i}. {qid}")
    
    # 显示权重分布（用于理解结果）
    print("\n各题目权重分布:")
    # 重新计算权重用于展示
    tag_weights = {tag: 0.0 for tag in all_tags}
    for tag in error_tags_str.split('*'):
        if tag in tag_weights:
            tag_weights[tag] += 1.0
    for tag in tag_weights:
        tag_weights[tag] *= 0.85
    
    question_weights = {}
    for qid, tags in defaultdict(list, [(q, t) for q, t in question_tag_list]).items():
        question_weights[qid] = 0.3 + sum(tag_weights.get(tag, 0) for tag in tags)
    
    for qid, weight in sorted(question_weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  题目{qid}: {weight:.2f}")