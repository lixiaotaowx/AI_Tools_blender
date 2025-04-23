import bpy
import os
from bpy.types import Menu, Operator, AddonPreferences
from bpy.props import StringProperty
import importlib.util
import random
from datetime import datetime
import subprocess
from functools import partial


bl_info = {
    "name": "AI助手-桃子",
    "category": "桃子",
    "author": "桃子",
    "blender": (4, 2, 0),
    "location": "View3D > F7",
    "description": "工具集",
    "doc_url": "https://github.com/lixiaotaowx/AI_Helper",
    "wiki_url": "https://github.com/lixiaotaowx/AI_Helper",
    "tracker_url": "https://github.com/lixiaotaowx/AI_Helper/issues",
    "version": ('2', '0', '1'),
}

# 获取脚本所在文件夹路径
script_dir = os.path.dirname(os.path.abspath(__file__))
path_txt_path = os.path.join(script_dir, 'path.txt')

# 八卦符号和对应的类型名称
bagua_symbols = [
    '☰  材质',  # 1
    '☱  网格',  # 2
    '☲  节点',  # 3
    '☳  相机',  # 4
    '☴  灯光',  # 5
    '☵  动画',  # 6
    '☶  渲染',  # 7
    '☷  脚本'   # 8
]


# 读取路径，如果文件不存在则使用默认路径
def read_path(use_custom_path):
    default_path = os.path.join(script_dir, 'scripts')
    if use_custom_path and os.path.exists(path_txt_path):
        try:
            with open(path_txt_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                print(f"从 path.txt 读取路径: {first_line}")  # Debug: Print the path read from file
                return first_line if first_line else default_path
        except Exception as e:
            print(f"读取 path.txt 时出错: {e}")  # Debug: Print error if reading fails
    print(f"使用默认路径: {default_path}")  # Debug: Print default path if path.txt does not exist or not using custom path
    return default_path


# 写入路径到path.txt文件
def write_path(path):
    try:
        with open(path_txt_path, 'w', encoding='utf-8') as f:
            f.write(path)
    except Exception as e:
        print(f"写入路径到 {path_txt_path} 时出错: {e}")


# 获取当前应使用的脚本路径（新增函数）
def get_current_script_path():
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
        path = read_path(prefs.use_custom_path)
        # 确保返回绝对路径
        abs_path = os.path.abspath(path)
        print(f"获取当前脚本路径: {abs_path}")
        print(f"路径是否存在: {os.path.exists(abs_path)}")
        # 如果目录不存在，尝试创建
        if not os.path.exists(abs_path):
            try:
                os.makedirs(abs_path, exist_ok=True)
                print(f"创建脚本目录: {abs_path}")
            except Exception as e:
                print(f"无法创建脚本目录: {e}")
        return abs_path
    except Exception as e:
        print(f"获取当前脚本路径时出错: {e}")
        # 返回默认路径
        default_path = os.path.join(script_dir, 'scripts')
        return os.path.abspath(default_path)


# 获取路径
folder_path = read_path(False)


# 执行 Python 文件中的内容
def execute_file_content(file_path):
    print(f"尝试执行文件: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件不存在: {file_path}")
        return
    
    try:
        # 使用Blender内置函数执行Python文件
        bpy.ops.script.python_file_run(filepath=file_path)
        print(f"成功执行文件: {file_path}")
    except Exception as e:
        print(f"执行文件时出错: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()


# 获取文件第一行内容作为按钮名字，去掉 # 符号
def get_first_line(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#'):
                return first_line.lstrip('#').strip()
            return first_line
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return "未知名称"


# 获取文件第二行内容作为提示信息，去掉 # 符号
def get_second_line(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 跳过第一行
            f.readline()
            second_line = f.readline().strip()
            if second_line.startswith('#'):
                return second_line.lstrip('#').strip()
            return ""
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return ""


# 获取文件第三行内容作为八卦分类，去掉 # 符号
def get_third_line(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 跳过前两行
            f.readline()
            f.readline()
            third_line = f.readline().strip()
            print(f"第三行原始内容: '{third_line}'")  # Debug: Print raw third line content
            if third_line.startswith('#'):
                third_line = third_line.lstrip('#').strip()  # 去除 # 和空格
                third_line = ''.join(third_line.split())  # 去除所有空白字符
                print(f"处理后的第三行内容: '{third_line}'")  # Debug: Print processed third line content
                try:
                    # 提取数字部分
                    index = int(''.join(filter(str.isdigit, third_line))) - 1  # 调整索引从1到8
                    if 0 <= index < 8:
                        return index
                    else:
                        print(f"八卦索引超出范围: {index}")  # Debug: Print out of range index
                except ValueError:
                    print(f"无效的八卦索引: {third_line}")  # Debug: Print invalid index
            else:
                print(f"第三行没有以 '#' 开头: {third_line}")  # Debug: Print if third line does not start with '#'
            return None
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None


operators = [[] for _ in range(8)]


# 定义 DynamicOperator 类
class DynamicOperator(bpy.types.Operator):
    bl_idname = "wm.dynamic_operator"
    bl_label = "Dynamic Operator"
    bl_description = ""
    path: bpy.props.StringProperty()

    def execute(self, context):
        # 首先检查path属性是否有效
        if self.path and os.path.isfile(self.path):
            print(f"使用操作符path属性执行脚本: {self.path}")
            execute_file_content(self.path)
            return {'FINISHED'}
            
        # 如果path无效，尝试从描述中获取路径
        if self.bl_description and "PATH:" in self.bl_description:
            try:
                # 从描述中提取路径 (格式: ... | PATH:路径)
                backup_path = self.bl_description.split("PATH:")[1].strip()
                if os.path.isfile(backup_path):
                    print(f"使用描述中的备份路径执行脚本: {backup_path}")
                    execute_file_content(backup_path)
                    return {'FINISHED'}
                else:
                    print(f"备份路径无效: {backup_path}")
            except Exception as e:
                print(f"从描述中提取路径失败: {e}")
        
        # 如果两种方法都失败，报错
        self.report({'ERROR'}, "无法找到有效的脚本文件路径")
        return {'CANCELLED'}

    def invoke(self, context, event):
        if event.type == 'RIGHTMOUSE':
            return context.window_manager.invoke_popup(self, width=200)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        # 从path或描述中提取文件名
        if self.path and os.path.exists(self.path):
            filename = os.path.basename(self.path)
        elif self.bl_description and "PATH:" in self.bl_description:
            try:
                backup_path = self.bl_description.split("PATH:")[1].strip()
                filename = os.path.basename(backup_path)
            except:
                filename = "未知文件"
        else:
            filename = "未知文件"
            
        layout.label(text=f"文件: {filename}")
        layout.operator("dynamic_operator.rename", text="重命名").path = self.path
        layout.operator("dynamic_operator.delete", text="删除").path = self.path
        layout.operator("dynamic_operator.open_in_editor", text="在文本编辑器中打开").path = self.path


# 动态更新 operators 列表
def update_operators():
    global operators
    operators = [[] for _ in range(8)]
    try:
        # 获取当前脚本路径
        current_path = get_current_script_path()
        
        print(f"======== 更新操作符 ========")
        print(f"使用文件夹路径: {current_path}")
        
        # 确保scripts目录存在
        if not os.path.exists(current_path):
            # 尝试创建目录
            try:
                os.makedirs(current_path, exist_ok=True)
                print(f"创建脚本目录: {current_path}")
            except Exception as e:
                print(f"无法创建脚本目录: {e}")
                return
            
        # 只处理.py文件    
        file_names = [file for file in os.listdir(current_path) if file.endswith(".py")]
        print(f"找到 {len(file_names)} 个脚本文件")
        
        if len(file_names) == 0:
            print(f"警告: 未找到脚本文件")
            return
            
        # 先获取现有注册的所有操作符ID，用于后续注销
        existing_op_ids = []
        for op_list in operators:
            for op_cls in op_list:
                existing_op_ids.append(op_cls.bl_idname)
                
        # 注销现有的所有操作符
        for op_id in existing_op_ids:
            # 构造类对象以便于注销
            if hasattr(bpy.types, op_id):
                cls_to_unreg = getattr(bpy.types, op_id)
                safe_unregister_class(cls_to_unreg)
        
        # 重新创建和注册操作符
        for index, file_name in enumerate(file_names, start=1):
            # 创建完整的绝对路径
            abs_path = os.path.abspath(os.path.join(current_path, file_name))
            
            # 验证文件存在
            if not os.path.isfile(abs_path):
                print(f"跳过无效文件: {abs_path}")
                continue
                
            try:
                # 读取脚本信息
                button_name = get_first_line(abs_path)
                tooltip = get_second_line(abs_path)
                bagua_index = get_third_line(abs_path)
                
                if bagua_index is None or not (0 <= bagua_index < 8):
                    print(f"跳过索引无效的文件: {file_name}")
                    continue
                
                # 创建操作符ID
                op_id = f"wm.dynamic_operator_{index}"
                
                # 在描述中添加路径作为备份 (格式: 原描述 | PATH:绝对路径)
                path_tooltip = f"{tooltip} | PATH:{abs_path}" if tooltip else f"PATH:{abs_path}"
                
                # 创建操作符
                op = type(
                    op_id,
                    (DynamicOperator,),
                    {
                        "bl_idname": op_id,
                        "bl_label": button_name,
                        "bl_description": path_tooltip,  # 在描述中嵌入路径
                        "path": abs_path  # 主要路径存储
                    }
                )
                
                # 使用安全注册函数
                safe_register_class(op)
                operators[bagua_index].append(op)
                
            except Exception as e:
                print(f"处理文件 {abs_path} 时出错: {e}")
                continue
                
    except Exception as e:
        print(f"更新操作符列表时出错: {e}")
        import traceback
        traceback.print_exc()

    # 验证结果
    for i, op_list in enumerate(operators):
        print(f"八卦索引 {i} 有 {len(op_list)} 个操作符")
    print("======== 更新操作符完成 ========")


# 定义 Pie 菜单
class VIEW3D_MT_PIE_template(Menu):
    bl_label = "iruler_CL"
    bl_idname = 'LI_Xiaotao_MT_menu'

    def draw(self, context):
        try:
            layout = self.layout
            pie = layout.menu_pie()
            print("绘制饼状菜单...")
            
            # 确保八卦子菜单都已正确注册
            available_menus = []
            for i in range(8):
                menu_name = f"WM_MT_bagua_menu_{i}"
                if hasattr(bpy.types, menu_name):
                    available_menus.append((i, menu_name))
                else:
                    print(f"警告: 子菜单 {menu_name} 未注册，将跳过")
            
            # 只添加已注册的菜单
            for i, menu_name in available_menus:
                try:
                    print(f"添加饼状菜单项: {bagua_symbols[i]} -> {menu_name}")
                    op = pie.operator("wm.call_menu", text=bagua_symbols[i])
                    op.name = menu_name
                except Exception as e:
                    print(f"添加菜单项 {bagua_symbols[i]} 失败: {e}")
                    # 添加一个空标签作为占位符，避免饼状菜单布局错乱
                    pie.label(text=f"{bagua_symbols[i]} (错误)")
        except Exception as e:
            print(f"绘制饼状菜单时出错: {e}")
            # 如果出现异常，添加错误提示，避免完全崩溃
            layout = self.layout
            layout.label(text=f"绘制菜单时出错: {str(e)[:30]}...")


# 饼状菜单给一个操作 方便设置快捷键
class WM_OT_CallPieMenu(bpy.types.Operator):
    bl_idname = "wm.call_pie_menu2"
    bl_label = "iruler_CL"

    def execute(self, context):
        print("调用饼状菜单...")
        try:
            bpy.ops.wm.call_menu_pie(name="LI_Xiaotao_MT_menu")
            print("饼状菜单调用成功")
        except Exception as e:
            print(f"调用饼状菜单时出错: {e}")
            self.report({'ERROR'}, f"调用菜单失败: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}


# Define a draw function for each bagua menu
def create_draw_function(index):
    def draw(self, context):
        print(f"绘制八卦子菜单: {bagua_symbols[index]} (索引: {index})")
        valid_operators = []
        
        # 过滤出有效的操作符
        for op_cls in operators[index]:
            if not op_cls.path or not os.path.isfile(op_cls.path):
                print(f"  - 跳过无效操作符: {op_cls.bl_idname}, 路径: {repr(op_cls.path)}")
                continue
            valid_operators.append(op_cls)
        
        if not valid_operators:
            self.layout.label(text="没有可用的操作符")
            return
        
        for op_cls in valid_operators:
            try:
                self.layout.operator(op_cls.bl_idname)
                print(f"  - 添加操作符到子菜单: {op_cls.bl_idname}")
            except Exception as e:
                print(f"  - 添加操作符到子菜单失败: {op_cls.bl_idname} - {e}")
    return draw


# 修改子菜单创建代码，确保只创建一次
# 在classes定义之前先清空已有的菜单类
classes = []

# 确保WM_MT_bagua_menu_X类只被创建一次
bagua_menu_classes = {}
for i in range(8):
    class_name = f"WM_MT_bagua_menu_{i}"
    if class_name not in globals():
        new_class = type(
            class_name,
            (bpy.types.Menu,),
            {
                "bl_idname": class_name,
                "bl_label": bagua_symbols[i],
                "draw": create_draw_function(i)
            }
        )
        globals()[class_name] = new_class
        bagua_menu_classes[class_name] = new_class
        print(f"定义八卦子菜单类: {class_name}")


# 定义新的操作
class OBJECT_OT_custom_option(bpy.types.Operator):
    bl_idname = "text.save_script"
    bl_label = "存为脚本"

    script_name: bpy.props.StringProperty(name="脚本名称")
    script_description: bpy.props.StringProperty(name="脚本描述")
    
    # 定义八卦分类为枚举类型的下拉列表
    bagua_items = [
        ('1', '☰ 材质', '材质相关脚本'),
        ('2', '☱ 网格', '网格相关脚本'),
        ('3', '☲ 节点', '节点相关脚本'),
        ('4', '☳ 相机', '相机相关脚本'),
        ('5', '☴ 灯光', '灯光相关脚本'),
        ('6', '☵ 动画', '动画相关脚本'),
        ('7', '☶ 渲染', '渲染相关脚本'),
        ('8', '☷ 脚本', '其他脚本'),
    ]
    
    bagua_index: bpy.props.EnumProperty(
        name="八卦分类",
        description="选择脚本的分类",
        items=bagua_items,
        default='1'
    )

    def invoke(self, context, event):
        text = context.space_data.text
        if not text or not text.as_string().strip():
            self.report({'INFO'}, "文本编辑器中没有文本。")
            return {'FINISHED'}
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    # 清理文件名，移除不合法字符
    def sanitize_filename(self, name):
        # 移除不允许在文件名中使用的字符
        import re
        name = re.sub(r'[\\/*?:"<>|]', "", name)
        # 确保不为空
        if not name.strip():
            name = "script"
        return name
    
    # 检查文件是否存在
    def file_exists(self, path, name):
        import os
        full_path = os.path.join(path, f"{name}.py")
        return os.path.exists(full_path)

    def execute(self, context):
        # 检查脚本名称是否有效
        if not self.script_name.strip():
            self.report({'ERROR'}, "请输入有效的脚本名称")
            return {'CANCELLED'}
        
        # 使用统一的路径获取函数
        current_path = get_current_script_path()
        
        # 获取当前文本编辑器中的文本
        text = context.space_data.text
        
        # 清理并生成文件名（使用脚本名称）
        file_name = self.sanitize_filename(self.script_name)
        
        # 检查文件是否已存在
        if self.file_exists(current_path, file_name):
            # 文件已存在，提示用户
            self.report({'ERROR'}, f"文件 '{file_name}.py' 已存在，请更改脚本名称")
            return {'CANCELLED'}
        
        # 构建完整文件路径
        file_path = os.path.join(current_path, f"{file_name}.py")
        
        # 获取文本内容
        text_content = text.as_string()
        
        # 获取选中的八卦索引
        bagua_idx = self.bagua_index  # 枚举值如 '1', '2' 等
        
        # 获取对应的类型名称（如"材质"，"网格"等）
        bagua_name = ""
        for item in self.bagua_items:
            if item[0] == bagua_idx:
                # 从"☰ 材质"中提取"材质"部分
                symbol_and_name = item[1].split()
                if len(symbol_and_name) > 1:
                    bagua_name = symbol_and_name[1]
                break
        
        print(f"保存脚本 - 八卦索引: {bagua_idx}, 类型名称: {bagua_name}")
        print(f"保存路径: {file_path}")
        
        # 构建新的文本内容，第三行格式为"# 1材质"（没有空格）
        new_text_content = f"# {self.script_name}\n# {self.script_description}\n# {bagua_idx}{bagua_name}\n{text_content}"

        # 首先保存文件，确保文件保存成功
        try:
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_text_content)
            print(f"脚本已成功保存到: {file_path}")
            save_success = True
        except Exception as e:
            print(f"保存脚本时出错: {e}")
            self.report({'ERROR'}, f"保存脚本时出错: {e}")
            return {'CANCELLED'}

        # 文件保存成功后，尝试重新加载插件
        # 将刷新操作放在单独的try-except块中，确保即使刷新失败也不会影响保存成功的消息
        if save_success:
            try:
                print("保存后尝试重新加载插件...")
                # 使用操作符重新加载插件
                try:
                    bpy.ops.iruler.reload_addon()
                    self.report({'INFO'}, f"脚本已保存到 {file_path} 并成功刷新列表")
                except Exception as inner_error:
                    print(f"重新加载插件时出错: {inner_error}")
                    import traceback
                    traceback.print_exc()
                    self.report({'WARNING'}, f"脚本已保存到 {file_path}，但刷新列表失败，请手动刷新。")
            except Exception as reload_error:
                print(f"重新加载插件时出错: {reload_error}")
                import traceback
                traceback.print_exc()
                # 即使刷新失败，也告诉用户文件已保存成功
                self.report({'WARNING'}, f"脚本已保存到 {file_path}，但刷新列表失败，请手动刷新。")

        return {'FINISHED'}




# 打开AI网站操作
class OpenAIWebsiteOperator(bpy.types.Operator):
    bl_idname = "iruler.open_ai_website"
    bl_label = "打开AI网站"

    url: bpy.props.StringProperty()

    def execute(self, context):
        try:
            print(f"打开网站: {self.url}")  # Debug: Print the URL being opened
            bpy.ops.wm.url_open(url=self.url)
            return {'FINISHED'}
        except Exception as e:
            print(f"打开网站时出错: {e}")  # Debug: Print error if opening fails
            return {'CANCELLED'}


# 定义新菜单
class TEXT_MT_custom_option_menu(bpy.types.Menu):
    bl_label = "AI辅助"
    bl_idname = "TEXT_MT_custom_option_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("text.save_script", text=f"存为脚本")
        
        layout.operator("iruler.open_script_directory", text="打开脚本目录")
        # 添加打开AI网站的子菜单
        layout.menu("TEXT_MT_ai_website_menu", text="打开AI网站")


# 定义AI网站子菜单
class TEXT_MT_ai_website_menu(bpy.types.Menu):
    bl_label = "AI网站"
    bl_idname = "TEXT_MT_ai_website_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("iruler.open_ai_website", text="豆包").url = "https://www.doubao.com"
        layout.operator("iruler.open_ai_website", text="Grok").url = "https://www.grok.com"
        layout.operator("iruler.open_ai_website", text="ChatGPT").url = "https://chat.openai.com"
        layout.operator("iruler.open_ai_website", text="Replika").url = "https://www.replika.ai"
        layout.operator("iruler.open_ai_website", text="Cleverbot").url = "https://www.cleverbot.com"


# 打开脚本目录操作
class IrulerOpenScriptDirectoryOperator(bpy.types.Operator):
    bl_idname = "iruler.open_script_directory"
    bl_label = "Open Script Directory"

    def execute(self, context):
        try:
            # 使用统一的路径获取函数
            current_path = get_current_script_path()
            print(f"打开脚本目录: {current_path}")
            bpy.ops.wm.path_open(filepath=current_path)
            return {'FINISHED'}
        except Exception as e:
            print(f"打开脚本目录失败: {e}")
            return {'CANCELLED'}


# 向TEXT_MT_editor_menus添加新菜单
def draw_custom_menu(self, context):
    self.layout.menu("TEXT_MT_custom_option_menu")


# 快捷键
addon_keymaps = []


def add_hotkey():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Screen', space_type='EMPTY')
    kmi = km.keymap_items.new("wm.call_pie_menu2", 'F7', 'PRESS', ctrl=False, shift=False)  # 修改为新的操作符ID
    addon_keymaps.append((km, kmi))


def remove_hotkey():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


# 完整的注销函数
def full_unregister():
    print("完全注销插件...")
    
    # 先尝试移除添加的UI元素
    try:
        bpy.types.TEXT_MT_editor_menus.remove(draw_custom_menu)
        print("从 TEXT_MT_editor_menus 移除自定义菜单。")
    except (AttributeError, ValueError) as e:
        print(f"从 TEXT_MT_editor_menus 移除自定义菜单失败: {e}")
    
    # 卸载动态操作符
    try:
        # 创建一个副本进行迭代，避免在迭代过程中修改列表
        all_operators = []
        for bagua_op_list in operators:
            all_operators.extend(bagua_op_list)
            
        # 迭代副本进行注销
        for op_cls in all_operators:
            safe_unregister_class(op_cls)
    except Exception as e:
        print(f"注销动态操作符失败: {e}")
    
    # 反向卸载所有类
    try:
        for cls in reversed(classes):
            safe_unregister_class(cls)
    except Exception as e:
        print(f"注销类列表失败: {e}")
    
    remove_hotkey()
    
    print("完全注销完成。")


# 修改 full_register 函数
def full_register():
    global classes  # 将global声明移到函数开头，确保在使用classes前声明
    print("开始完全注册...")
    
    # 先清理classes列表中重复的子菜单类
    class_names = set()
    unique_classes = []
    for cls in classes:
        if cls.__name__ not in class_names:
            class_names.add(cls.__name__)
            unique_classes.append(cls)
    
    # 替换classes列表为去重后的列表
    classes = unique_classes
    
    print(f"清理后classes列表中有 {len(classes)} 个类等待注册")
    
    # 先更新操作符列表（在注册菜单之前）
    update_operators()
    
    # 确保八卦子菜单类先注册
    for cls in classes[:]:
        if cls.__name__.startswith("WM_MT_bagua_menu_"):
            safe_register_class(cls)
    
    # 再注册其他类
    for cls in classes[:]:
        if not cls.__name__.startswith("WM_MT_bagua_menu_"):
            safe_register_class(cls)
    
    # 添加到文本编辑器菜单
    try:
        bpy.types.TEXT_MT_editor_menus.append(draw_custom_menu)
        print("将自定义菜单添加到 TEXT_MT_editor_menus。")
    except Exception as e:
        print(f"添加菜单到 TEXT_MT_editor_menus 失败: {e}")
    
    add_hotkey()
    
    # 验证子菜单是否已注册
    for i in range(8):
        menu_name = f"WM_MT_bagua_menu_{i}"
        if hasattr(bpy.types, menu_name):
            print(f"子菜单 {menu_name} 已正确注册")
        else:
            print(f"警告: 子菜单 {menu_name} 未注册!")
    
    print("注册完成。")


# 重新加载插件的处理程序
@bpy.app.handlers.persistent
def reload_addon_handler(dummy):
    full_unregister()
    full_register()
    bpy.app.handlers.load_post.remove(reload_addon_handler)
    bpy.ops.info.select_all(action='DESELECT')
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


# 重新加载插件操作
class IrulerReloadAddonOperator(Operator):
    bl_idname = "iruler.reload_addon"
    bl_label = "重新加载插件"

    def execute(self, context):
        full_unregister()
        full_register()
        self.report({'INFO'}, "插件已重新加载")
        return {'FINISHED'}


# 保存路径操作
class IrulerSavePathOperator(Operator):
    bl_idname = "iruler.save_path"
    bl_label = "保存路径"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        write_path(prefs.folder_path)  # 同步更新 path.txt
        full_unregister()  # 重新注销
        full_register()  # 重新注册
        self.report({'INFO'}, "路径已保存并刷新")
        return {'FINISHED'}


# 实现重命名操作
class DynamicOperatorRename(bpy.types.Operator):
    bl_idname = "dynamic_operator.rename"
    bl_label = "重命名操作符"

    path: bpy.props.StringProperty()

    new_name: bpy.props.StringProperty(name="新名称")
    new_description: bpy.props.StringProperty(name="新描述")

    def invoke(self, context, event):
        # 读取当前名称和描述
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines and lines[0].startswith('# '):
                    self.new_name = lines[0].lstrip('# ').strip()
                if len(lines) > 1 and lines[1].startswith('# '):
                    self.new_description = lines[1].lstrip('# ').strip()
        except Exception as e:
            print(f"读取文件信息时出错: {e}")
            
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        try:
            with open(self.path, 'r+', encoding='utf-8') as f:
                lines = f.readlines()
                lines[0] = f"# {self.new_name}\n"
                lines[1] = f"# {self.new_description}\n"
                f.seek(0)
                f.writelines(lines)
                
            # 重新加载插件以更新列表
            bpy.ops.iruler.reload_addon()
            
            self.report({'INFO'}, "重命名成功")
        except Exception as e:
            self.report({'ERROR'}, f"重命名失败: {e}")
        return {'FINISHED'}


# 实现删除操作
class DynamicOperatorDelete(bpy.types.Operator):
    bl_idname = "dynamic_operator.delete"
    bl_label = "删除操作符"
    bl_options = {'REGISTER'}

    path: bpy.props.StringProperty()
    confirm: bpy.props.BoolProperty(
        name="确认删除",
        description="确认删除此脚本",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        
        # 显示文件名，让用户知道要删除哪个文件
        if self.path:
            filename = os.path.basename(self.path)
            layout.label(text=f"您确定要删除脚本 '{filename}' 吗?")
            
        # 确认选项
        layout.prop(self, "confirm")
        layout.label(text="⚠️ 此操作不可撤销！", icon='ERROR')

    def execute(self, context):
        if not self.confirm:
            self.report({'WARNING'}, "删除操作已取消")
            return {'CANCELLED'}
        
        print(f"准备删除文件: {self.path}")
        
        # 确保有有效路径
        if not self.path or not os.path.exists(self.path):
            self.report({'ERROR'}, "找不到要删除的文件")
            return {'CANCELLED'}
        
        # 保存文件名，用于错误报告
        filename = os.path.basename(self.path)
        
        try:
            # 先从Blender的文本数据中移除引用，以避免资源占用

            # 删除文件
            os.remove(self.path)
            print(f"文件已成功删除: {self.path}")
            
            # 确保已加载的资源被释放
            import time
            time.sleep(0.2)  # 增加延迟时间确保资源释放
            
            # 手动垃圾回收以确保所有引用被释放
            import gc
            gc.collect()
            
            # 使用更安全的方式重新加载插件，放在单独的try块中
            try:
                print("正在以安全模式重新加载插件...")
                
                # 使用try-finally确保即使刷新过程出错，用户也能知道文件已被删除
                try:
    
                    # 直接调用full_unregister和full_register，而不是通过操作符
                    full_unregister()
                    full_register()
                    print("插件重新加载成功")
                    
                except Exception as reload_error:
                    print(f"重新加载插件时出错: {reload_error}")
                    import traceback
                    traceback.print_exc()
                    
                    # 尝试使用操作符方式作为备选方案
                    try:
                        bpy.ops.iruler.reload_addon()
                        print("通过操作符成功重新加载插件")
                    except:
                        print("备选重载方法也失败了")
                        self.report({'WARNING'}, f"文件 {filename} 已删除，但刷新列表失败。请手动刷新。")
                        return {'FINISHED'}  # 仍然返回FINISHED，因为文件已成功删除
                
            except Exception as e:
                print(f"刷新过程中发生未预期的错误: {e}")
                self.report({'WARNING'}, f"文件 {filename} 已删除，但自动刷新失败。请手动刷新。")
                return {'FINISHED'}  # 仍然返回FINISHED，因为文件已成功删除
            
            self.report({'INFO'}, f"文件 {filename} 已成功删除并刷新列表")
            
        except PermissionError:
            self.report({'ERROR'}, f"没有权限删除文件 {filename}，文件可能被其他程序占用")
            return {'CANCELLED'}
        except Exception as e:
            print(f"删除文件时出错: {e}")
            self.report({'ERROR'}, f"删除 {filename} 失败: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}


# 实现在文本编辑器中打开操作
class DynamicOperatorOpenInEditor(bpy.types.Operator):
    bl_idname = "dynamic_operator.open_in_editor"
    bl_label = "在文本编辑器中打开"
    bl_options = {'REGISTER'}

    path: bpy.props.StringProperty()

    def execute(self, context):
        try:
            # 确保路径有效
            script_path = self.path
            if not os.path.exists(script_path):
                # 尝试使用当前脚本路径重新构建
                current_base_path = get_current_script_path()
                filename = os.path.basename(script_path)
                alternative_path = os.path.join(current_base_path, filename)
                print(f"- 尝试替代路径: {alternative_path}")
                
                if os.path.exists(alternative_path):
                    script_path = alternative_path
                    print(f"- 使用替代路径: {script_path}")
                else:
                    self.report({'ERROR'}, f"找不到脚本文件: {script_path}")
                    return {'CANCELLED'}
            
            # 获取文件名
            text_name = os.path.basename(script_path)
            
            # 先加载文件到Blender的文本数据中
            text = None
            for txt in bpy.data.texts:
                if txt.filepath == script_path:
                    text = txt
                    break
            
            if text is None:
                text = bpy.data.texts.load(script_path)
                print(f"已加载文件: {text_name}")
            else:
                print(f"文件已存在于Blender中: {text_name}")
            
            # 查找所有文本编辑器区域并打开文件
            found_text_editor = False
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'TEXT_EDITOR':
                        for space in area.spaces:
                            if space.type == 'TEXT_EDITOR':
                                space.text = text
                                found_text_editor = True
                                print(f"已在现有文本编辑器中打开: {text_name}")
            
            # 如果没有找到文本编辑器，创建新窗口
            if not found_text_editor:
                try:
                    print("未找到现有文本编辑器，创建新窗口...")
                    
                    # 创建新窗口
                    bpy.ops.wm.window_new()
                    
                    # 在新创建的窗口中执行操作
                    override = context.copy()
                    # 获取最新创建的窗口
                    override['window'] = context.window_manager.windows[-1]
                    
                    # 获取新窗口中的第一个区域
                    area = override['window'].screen.areas[0]
                    override['area'] = area
                    
                    # 设置区域类型为文本编辑器
                    with context.temp_override(**override):
                        area.type = 'TEXT_EDITOR'
                        # 确保区域类型已更改
                        print(f"区域类型已设置为: {area.type}")
                        
                        # 在文本编辑器中设置文本
                        for space in area.spaces:
                            if space.type == 'TEXT_EDITOR':
                                space.text = text
                                print(f"已在新窗口的文本编辑器中设置文本: {text_name}")
                                break
                    
                    self.report({'INFO'}, f"已在新窗口中打开: {text_name}")
                except Exception as e:
                    print(f"创建新窗口或设置文本编辑器失败: {e}")
                    self.report({'WARNING'}, f"已加载文件 {text_name}，但无法创建新窗口。请手动切换到文本编辑器查看。")
            else:
                self.report({'INFO'}, f"已在现有文本编辑器中打开: {text_name}")
            
            return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"打开失败: {e}")
            print(f"打开文件时出错: {e}")
            return {'CANCELLED'}


# 更新路径回调函数 - 当用户更改文件夹路径时自动保存
def update_folder_path(self, context):
    print("自动保存脚本目录路径: " + self.folder_path)
    # 写入新路径到path.txt
    write_path(self.folder_path)
    # 如果已启用自定义路径，则重新加载插件以应用新路径
    if self.use_custom_path:
        try:
            # 先注销
            full_unregister()
            # 再重新注册
            full_register()
            print("路径已更新并自动应用")
        except Exception as e:
            print(f"应用新路径时出错: {e}")
            import traceback
            traceback.print_exc()


# 在IrulerAddonPreferences类的定义前，添加更新回调函数
def update_use_custom_path(self, context):
    print("路径设置已更改，正在刷新...")
    # 重新加载插件以应用新路径
    try:
        # 先注销
        full_unregister()
        # 再重新注册
        full_register()
        print("路径设置更改完成，插件已刷新")
    except Exception as e:
        print(f"路径设置更改时刷新插件失败: {e}")
        import traceback
        traceback.print_exc()


# 添加一个新的设置操作符类
class DynamicOperatorSettings(bpy.types.Operator):
    bl_idname = "dynamic_operator.settings"
    bl_label = "脚本设置"

    path: bpy.props.StringProperty()
    script_name: bpy.props.StringProperty(name="脚本名称")
    script_description: bpy.props.StringProperty(name="脚本描述")
    
    # 定义八卦分类为枚举类型的下拉列表
    bagua_items = [
        ('1', '☰ 材质', '材质相关脚本'),
        ('2', '☱ 网格', '网格相关脚本'),
        ('3', '☲ 节点', '节点相关脚本'),
        ('4', '☳ 相机', '相机相关脚本'),
        ('5', '☴ 灯光', '灯光相关脚本'),
        ('6', '☵ 动画', '动画相关脚本'),
        ('7', '☶ 渲染', '渲染相关脚本'),
        ('8', '☷ 脚本', '其他脚本'),
    ]
    
    bagua_index: bpy.props.EnumProperty(
        name="八卦分类",
        description="选择脚本的分类",
        items=bagua_items,
        default='1'
    )

    def invoke(self, context, event):
        # 读取当前脚本信息
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines and lines[0].startswith('# '):
                    self.script_name = lines[0].lstrip('# ').strip()
                if len(lines) > 1 and lines[1].startswith('# '):
                    self.script_description = lines[1].lstrip('# ').strip()
                if len(lines) > 2 and lines[2].startswith('# '):
                    third_line = lines[2].lstrip('#').strip()
                    try:
                        # 提取数字部分
                        bagua_num = ''.join(filter(str.isdigit, third_line))
                        if bagua_num and 1 <= int(bagua_num) <= 8:
                            self.bagua_index = bagua_num
                    except ValueError:
                        pass
        except Exception as e:
            print(f"读取文件信息时出错: {e}")
            
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        try:
            # 读取原文件内容
            with open(self.path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 获取脚本内容 (第四行开始)
            script_content = ''.join(lines[3:]) if len(lines) > 3 else ""
            
            # 获取对应的类型名称（如"材质"，"网格"等）
            bagua_name = ""
            for item in self.bagua_items:
                if item[0] == self.bagua_index:
                    # 从"☰ 材质"中提取"材质"部分
                    symbol_and_name = item[1].split()
                    if len(symbol_and_name) > 1:
                        bagua_name = symbol_and_name[1]
                    break
                    
            # 构建新的文件内容
            new_content = f"# {self.script_name}\n# {self.script_description}\n# {self.bagua_index}{bagua_name}\n{script_content}"
            
            # 写回文件
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            # 重新加载插件以更新列表
            bpy.ops.iruler.reload_addon()
            
            self.report({'INFO'}, "脚本设置已更新")
        except Exception as e:
            self.report({'ERROR'}, f"更新脚本设置失败: {e}")
        return {'FINISHED'}


# 在IrulerAddonPreferences类定义中添加get_script_files方法
def get_script_files(self):
    script_files = []
    current_path = get_current_script_path()
    
    if os.path.exists(current_path):
        for file_name in os.listdir(current_path):
            if file_name.endswith(".py"):
                file_path = os.path.join(current_path, file_name)
                if os.path.isfile(file_path):
                    # 获取脚本信息
                    script_name = get_first_line(file_path)
                    bagua_index = get_third_line(file_path)
                    if bagua_index is not None:
                        bagua_index += 1  # 调整回1-8
                    else:
                        bagua_index = "?"
                        
                    script_files.append({
                        "name": script_name,
                        "path": file_path,
                        "bagua": bagua_index
                    })
    
    # 按名称排序
    script_files.sort(key=lambda x: x["name"].lower())
    return script_files


# 修改IrulerAddonPreferences类的draw方法
def draw(self, context):
    layout = self.layout
    
    # 路径设置
    box = layout.box()
    box.label(text="路径设置")
    box.prop(self, "use_custom_path")
    # 添加提示信息，使用ERROR图标作为叹号
    box.label(text="非服务器共享用户一般不需要自定义路径", icon='INFO')
    box.prop(self, "folder_path")
    # 不再需要"保存路径"按钮，因为路径会自动保存
    # 保留"重新加载"按钮作为手动刷新选项
    
    box.label(text="提示: 修改路径会自动保存并应用", icon='INFO')
    box.operator("iruler.reload_addon", text="重新加载插件")
    
    # 脚本列表
    script_box = layout.box()
    script_box.label(text="脚本列表")
    
    # 获取脚本文件
    script_files = self.get_script_files()
    
    if not script_files:
        script_box.label(text="没有找到脚本文件")
    else:
        # 表头
        header_row = script_box.row()
        header_row.label(text="名称")
        header_row.label(text="分类")
        header_row.label(text="操作")
        
        # 列表
        for script in script_files:
            row = script_box.row()
            # 显示脚本名称
            row.label(text=script["name"])
            
            # 显示分类
            if isinstance(script["bagua"], int) and 1 <= script["bagua"] <= 8:
                row.label(text=bagua_symbols[script["bagua"]-1])
            else:
                row.label(text="未知分类")
            
            # 操作按钮
            buttons = row.row(align=True)
            op = buttons.operator("dynamic_operator.delete", text="删除", icon='TRASH')
            op.path = script["path"]
            
            op = buttons.operator("dynamic_operator.open_in_editor", text="编辑", icon='TEXT')
            op.path = script["path"]
            
            op = buttons.operator("dynamic_operator.settings", text="设置", icon='PREFERENCES')
            op.path = script["path"]


# 修改IrulerAddonPreferences类定义
class IrulerAddonPreferences(AddonPreferences):
    bl_idname = __name__

    folder_path: StringProperty(
        name="脚本文件夹",
        subtype='DIR_PATH',
        default=os.path.join(script_dir, 'scripts'),
        update=update_folder_path  # 添加更新回调，自动保存路径
    )
    
    use_custom_path: bpy.props.BoolProperty(
        name="使用自定义路径",
        description="是否使用自定义路径而不是默认路径",
        default=False,
        update=update_use_custom_path  # 添加更新回调
    )

    draw = draw
    get_script_files = get_script_files


# 在initialize_classes函数中添加DynamicOperatorSettings
def initialize_classes():
    global classes
    # 先清空classes列表
    classes = []
    
    # 先添加所有八卦子菜单类
    for i in range(8):
        class_name = f"WM_MT_bagua_menu_{i}"
        if class_name in bagua_menu_classes:
            classes.append(bagua_menu_classes[class_name])
    
    # 然后添加其他类
    classes.append(VIEW3D_MT_PIE_template)
    classes.append(WM_OT_CallPieMenu)
    classes.append(OBJECT_OT_custom_option)
    classes.append(TEXT_MT_custom_option_menu)
    classes.append(IrulerOpenScriptDirectoryOperator)
    classes.append(OpenAIWebsiteOperator)
    classes.append(TEXT_MT_ai_website_menu)
    classes.append(DynamicOperatorRename)
    classes.append(DynamicOperatorDelete)
    classes.append(DynamicOperatorOpenInEditor)
    classes.append(DynamicOperatorSettings)  # 添加新的设置操作符


# 在register函数之前调用initialize_classes
initialize_classes()

def register():
    print("注册插件类...")
    
    # 确保先注册这些基本类
    safe_register_class(IrulerAddonPreferences)
    safe_register_class(IrulerSavePathOperator)
    safe_register_class(IrulerReloadAddonOperator)
    
    # 添加处理程序并调用full_register
    try:
        bpy.app.handlers.load_post.append(reload_addon_handler)
        print("将 reload_addon_handler 添加到 load_post 处理程序。")
    except Exception as e:
        print(f"添加 reload_addon_handler 到 load_post 失败: {e}")
    
    # 调用full_register前，确保DynamicOperator子类已注册
    safe_register_class(DynamicOperatorRename)
    safe_register_class(DynamicOperatorDelete)
    safe_register_class(DynamicOperatorOpenInEditor)
    
    full_register()


def unregister():
    print("注销插件类...")
    
    # 先尝试移除添加的UI元素
    try:
        bpy.types.TEXT_MT_editor_menus.remove(draw_custom_menu)
        print("从 TEXT_MT_editor_menus 移除自定义菜单。")
    except (AttributeError, ValueError) as e:
        print(f"从 TEXT_MT_editor_menus 移除自定义菜单失败: {e}")
    
    # 卸载动态操作符
    try:
        # 创建一个副本进行迭代，避免在迭代过程中修改列表
        all_operators = []
        for bagua_op_list in operators:
            all_operators.extend(bagua_op_list)
            
        # 迭代副本进行注销
        for op_cls in all_operators:
            safe_unregister_class(op_cls)
    except Exception as e:
        print(f"注销动态操作符失败: {e}")
    
    # 反向卸载所有类
    try:
        for cls in reversed(classes):
            safe_unregister_class(cls)
    except Exception as e:
        print(f"注销类列表失败: {e}")
    
    remove_hotkey()

    # 移除处理程序
    try:
        if reload_addon_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(reload_addon_handler)
            print("从 load_post 处理程序中移除 reload_addon_handler。")
    except Exception as e:
        print(f"移除 reload_addon_handler 失败: {e}")
    
    # 最后注销基本类
    safe_unregister_class(IrulerReloadAddonOperator)
    safe_unregister_class(IrulerSavePathOperator)
    safe_unregister_class(IrulerAddonPreferences)


# 安全类注册函数 - 仅在类未注册时注册
def safe_register_class(cls):
    if not hasattr(bpy.types, cls.bl_idname):
        try:
            bpy.utils.register_class(cls)
            print(f"成功注册类: {cls.bl_idname}")
        except Exception as e:
            print(f"注册类 {cls.bl_idname} 失败: {e}")

# 安全类注销函数 - 仅在类已注册时注销
def safe_unregister_class(cls):
    if hasattr(bpy.types, cls.bl_idname):
        try:
            bpy.utils.unregister_class(cls)
            print(f"成功注销类: {cls.bl_idname}")
        except Exception as e:
            print(f"注销类 {cls.bl_idname} 失败: {e}")

    