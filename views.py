import ast
import json
import logging
import random
from collections import defaultdict

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from app01 import models

# 配置日志
logger = logging.getLogger('myapp')
# 可以在 settings.py 里统一配置日志格式、输出位置等，这里先简单示例手动设置
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建文件处理器，将日志写入文件（可根据需要调整路径）
file_handler = logging.FileHandler('django_app.log')
file_handler.setFormatter(formatter)

# 创建控制台处理器，将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)  # 设置日志级别，开发环境可设为 DEBUG，生产环境可设为 INFO 等


def xxxx(request):
    logger.info("触发 xxxx 视图，重定向到 /home/")
    return redirect('/home/')


# 主页
@login_required()
def home(request):
    try:
        logger.info(f"用户 {request.user.username} 访问主页 - 方法: {request.method}")
        return render(request, 'home.html')
    except Exception as e:
        logger.error(f"用户 {request.user.username} 主页渲染失败: {str(e)}", exc_info=True)
        return HttpResponse("页面加载出错，请稍后再试")


# 注册
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.info(f"开始处理注册请求，用户名: {username}")
        try:
            use = User.objects.create_user(username=username, password=password)
            if use:
                logger.info(f"用户 {username} 注册成功，重定向到 /login/")
                return redirect('/login/')
        except Exception as e:
            logger.error(f"用户 {username} 注册失败: {str(e)}", exc_info=True)
            return HttpResponse("注册失败，请检查用户名是否已存在或其他错误")
    logger.info("渲染注册页面（GET 请求）")
    return render(request, 'register.html')


# 登录页面
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.info(f"处理登录请求，用户名: {username}")
        use_obj = auth.authenticate(request, username=username, password=password)
        if use_obj:
            auth.login(request, use_obj)
            if not models.Message.objects.filter(message_id=request.user.pk).exists():
                models.Message.objects.create(message_id=request.user.pk, wrong='*', right='*')
            logger.info(f"用户 {username} 登录成功，渲染 home.html")
            return render(request, 'home.html')
        else:
            logger.warning(f"用户 {username} 登录失败，用户名或密码错误")
            return HttpResponse("用户名或密码错误")
    logger.info("渲染登录页面（GET 请求）")
    return render(request, 'login.html', locals())


# 修改密码
@login_required()
def set_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        re_password = request.POST.get('re_password')
        logger.info(f"用户 {request.user.username} 开始修改密码")
        if new_password == re_password:
            is_right = request.user.check_password(old_password)  # 注意这里之前代码传参是字符串 'old_password'，应该传变量
            if is_right:
                request.user.set_password(new_password)
                request.user.save()
                logger.info(f"用户 {request.user.username} 密码修改成功，重定向到 /login/")
                return redirect('/login/')
            else:
                logger.warning(f"用户 {request.user.username} 旧密码错误")
                return HttpResponse('旧密码错误')
        else:
            logger.warning(f"用户 {request.user.username} 两次输入密码不一致")
            return HttpResponse('两次密码不一致')
    logger.info(f"用户 {request.user.username} 渲染修改密码页面（GET 请求）")
    return render(request, 'set_password.html', locals())


# 注销账号
@login_required()
def logout(request):
    logger.info(f"用户 {request.user.username} 执行注销操作")
    auth.logout(request)
    logger.info("注销成功，重定向到 /login/")
    return redirect('/login/')


# 开始挑战
@login_required()
def start(request):
    # 获取用户每次完成之后的对题集和错题集
    if request.method == "POST":
        userAnswers = request.POST.get('user_answers')
        data = json.loads(userAnswers)
        str000 = ''
        str111 = ''
        print(data)
        for item in data:
            if not item['isCorrect']:
                history_obj = models.History.objects.create(name_user=request.user.username,
                                                            user_question=item['questionText'],
                                                            user_choice=item['userChoice'],
                                                            question_answer=item['correctAnswer'],
                                                            question_detail=models.Main.objects.filter(
                                                                id=item['questionPk']).first().detail, question_pk=list(
                        models.Main.objects.filter(id=item['questionPk']).first().knowledge.all().values_list(
                            'knowledge_pot')))
                history_obj.save()
                know = models.Main.objects.filter(id=item['questionPk']).first().knowledge.all()
                for k in know:
                    if k.knowledge_pot != "其他":
                        str000 += k.knowledge_pot + '*'
            else:
                know = models.Main.objects.filter(id=item['questionPk']).first().knowledge.all()
                for k in know:
                    if k.knowledge_pot != "其他":
                        str111 += k.knowledge_pot + '*'

        re_wrong = models.Message.objects.filter(message_id=request.user.pk).first().wrong
        re_right = models.Message.objects.filter(message_id=request.user.pk).first().right
        str000 = re_wrong + str000
        str111 = re_right + str111
        rows_affected = models.Message.objects.update(wrong=str000, right=str111)
        logger.info(f"已更新 {rows_affected} 条记录")  # 使用 info 级别记录更新信息
    dif = request.GET.get('difficulty')
    logger.info(f"用户 {request.user.username} 开始挑战，难度: {dif}")
    # 下面是用户选择开始挑战进行的程序
    body = []
    if dif == 'easy':
        body = list(models.Main.objects.filter(hard__range=[0, 3]))
    elif dif == 'medium':
        body = list(models.Main.objects.filter(hard__range=[4, 6]))
    else:
        body = list(models.Main.objects.filter(hard__range=[7, 10]))
    try:
        worry_obj = models.Message.objects.filter(message_id=request.user.pk).first().wrong
        wrong_lst0 = worry_obj.split('*')[1:][:-1]
        dic0 = {'语言基础': 1, '数据类型与变量': 2, '运算符与表达式': 3, '控制结构': 4, '字符串与字符': 5,
                ' 列表与元组': 6, '字典与集合': 7, '函数': 8, '模块与包': 9, '面向对象': 10, '文件操作': 11,
                '异常处理': 12, '图形用户界面': 13, '程序结构': 14, '编译过程': 15, '运行时异常': 16, 'C++关键字': 17,
                '指针': 18, '引用': 19, '优先级': 20, '逻辑运算': 21, '表达式': 22, '数组': 23, '结构体': 24,
                '构造与析构': 25, '构造函数': 26, '析构函数': 27, '静态成员': 28, '成员函数': 29, '友元': 30,
                '运算符重载': 31, '继承': 32, '虚函数': 33, '抽象类': 34, '模板': 35, 'I/O流': 36, '封装': 37,
                '代码重用': 38, '虚继承': 39, '动态内存': 40, '数据隐藏': 41, '其他': 42}
        for i in range(len(wrong_lst0)):
            wrong_lst0[i] = str(dic0[wrong_lst0[i]])
        sum_body = []
        for i in body:
            for j in i.knowledge.all():
                sum_body.append((str(i.pk), str(dic0[j.knowledge_pot])))
        error_tags_str = wrong_lst0
        question_tag_list = sum_body
        all_tags = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                    '19',
                    '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
                    '36', '37',
                    '38', '39', '40', '41', '42']
        next_questions = get_next_questions(error_tags_str, all_tags, question_tag_list, count=10)
        next_questions = list(map(int, next_questions))
        x1 = models.Main.objects.filter(id=next_questions[0]).first()
        x2 = models.Main.objects.filter(id=next_questions[1]).first()
        x3 = models.Main.objects.filter(id=next_questions[2]).first()
        x4 = models.Main.objects.filter(id=next_questions[3]).first()
        x5 = models.Main.objects.filter(id=next_questions[4]).first()
        x6 = models.Main.objects.filter(id=next_questions[5]).first()
        x7 = models.Main.objects.filter(id=next_questions[6]).first()
        x8 = models.Main.objects.filter(id=next_questions[7]).first()
        x9 = models.Main.objects.filter(id=next_questions[8]).first()
        x10 = models.Main.objects.filter(id=next_questions[9]).first()
        x1_category = ""
        x2_category = ""
        x3_category = ""
        x4_category = ""
        x5_category = ""
        x6_category = ""
        x7_category = ""
        x8_category = ""
        x9_category = ""
        x10_category = ""
        for i in x1.knowledge.all():
            x1_category += str(i.knowledge_pot) + " "
        for i in x2.knowledge.all():
            x2_category += str(i.knowledge_pot) + " "
        for i in x3.knowledge.all():
            x3_category += str(i.knowledge_pot) + " "
        for i in x4.knowledge.all():
            x4_category += str(i.knowledge_pot) + " "
        for i in x5.knowledge.all():
            x5_category += str(i.knowledge_pot) + " "
        for i in x6.knowledge.all():
            x6_category += str(i.knowledge_pot) + " "
        for i in x7.knowledge.all():
            x7_category += str(i.knowledge_pot) + " "
        for i in x8.knowledge.all():
            x8_category += str(i.knowledge_pot) + " "
        for i in x9.knowledge.all():
            x9_category += str(i.knowledge_pot) + " "
        for i in x10.knowledge.all():
            x10_category += str(i.knowledge_pot) + " "
        logger.info(f"用户 {request.user.username} 挑战题目加载完成，准备渲染 start.html")
        return render(request, 'start.html', locals())
    except Exception as e:
        logger.error(f"用户 {request.user.username} 加载挑战题目失败: {str(e)}", exc_info=True)
        return HttpResponse("题目加载出错，请稍后再试")


# 外部填入数据
def get_data(request):
    if request.method == 'POST':
        title = request.POST['title']
        a = str(request.POST['a']).upper()
        b = str(request.POST['b']).upper()
        c = str(request.POST['c']).upper()
        d = str(request.POST['d']).upper()
        hard = int(request.POST['hard'])
        answer = str(request.POST['real']).upper()
        detail = request.POST['answer']
        know = request.POST.getlist('xxx')
        know = list(map(int, know))
        logger.info(f"开始处理外部填入数据请求，标题: {title}")
        try:
            main_obj = models.Main.objects.create(question=title, answer=answer, detail=detail, choice_a=a, choice_b=b,
                                                  choice_c=c, choice_d=d, hard=hard)
            main_obj.knowledge.add(*know)
            body = models.Knowledge.objects.all()
            logger.info(f"外部数据填入成功，数据标题: {title}")
            return render(request, 'get_data.html', locals())
        except Exception as e:
            logger.error(f"外部数据填入失败: {str(e)}", exc_info=True)
            return HttpResponse("数据填入失败，请检查参数是否正确")
    body = models.Knowledge.objects.all()
    logger.info("渲染 get_data.html 页面（GET 请求）")
    return render(request, 'get_data.html', locals())


# 外部写入数据
def index(request):
    data = [
        # 这里 data 列表内容你可以根据实际补充，当前为空，执行时可能无实际操作
    ]
    dic = {'语言基础': 1, '数据类型与变量': 2, '运算符与表达式': 3, '控制结构': 4, '字符串与字符': 5, ' 列表与元组': 6,
           '字典与集合': 7, '函数': 8, '模块与包': 9, '面向对象': 10, '文件操作': 11, '异常处理': 12,
           '图形用户界面': 13, '程序结构': 14, '编译过程': 15, '运行时异常': 16, 'C++关键字': 17, '指针': 18,
           '引用': 19, '优先级': 20, '逻辑运算': 21, '表达式': 22, '数组': 23, '结构体': 24, '构造与析构': 25,
           '构造函数': 26, '析构函数': 27, '静态成员': 28, '成员函数': 29, '友元': 30, '运算符重载': 31, '继承': 32,
           '虚函数': 33, '抽象类': 34, '模板': 35, 'I/O流': 36, '封装': 37, '代码重用': 38, '虚继承': 39,
           '动态内存': 40, '数据隐藏': 41, '其他': 42}
    logger.info("开始处理外部写入数据请求")
    for i in data:
        try:
            lst0 = []
            # print(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
            main_obj = models.Main.objects.create(question=i[0], choice_a=i[1], choice_b=i[2], choice_c=i[3],
                                                  choice_d=i[4], answer=i[5], detail=i[6], hard=int(i[7]))
            for j in i[8]:
                if j in dic.keys():
                    lst0.append(dic[j])
            if not lst0:
                lst0.append(42)
            # print(lst0)
            main_obj.knowledge.add(*lst0)
            main_obj.save()
            logger.info(f"外部数据写入成功，数据标题: {i[0]}")
        except Exception as e:
            logger.error(f"外部数据 {i[0]} 写入失败: {str(e)}", exc_info=True)
    return HttpResponse("Hello, world. You're at the")


# 选择难度
@login_required()
def choice_hard(request):
    return render(request, 'choice_hard.html')


@login_required()
def history(request):
    list_know = []
    history_obj = models.History.objects.filter(name_user=request.user.username).all()
    for i in history_obj:
        temp_obj = []
        # 将字符串解析为 Python 列表（包含元组）
        result = ast.literal_eval(i.question_pk)
        # 转换为纯列表结构（可选）
        pure_list = [list(t) for t in result]
        for j in pure_list:
            temp_obj.append(j[0])
        for k in temp_obj:
            list_know.append(temp_obj[0])
    list_know = list(set(list_know))
    len = history_obj.__len__()
    return render(request, 'history.html', locals())


def get_next_questions(error_tags, all_tags, question_tag_list, count=10,
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
        normalized_weight = (question_weights[qid] - min_weight) / (
                max_weight - min_weight) if max_weight > min_weight else 0.5

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
