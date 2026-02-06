# Python 编码规范

## 1. PEP 8 - Python 官方编码风格指南

PEP 8 是 Python 官方推荐的编码风格指南，是最重要的 Python 编码规范。

### 命名约定
- **变量和函数名**: 使用小写字母和下划线 (`snake_case`)
- **类名**: 使用驼峰命名法 (`CamelCase`)
- **常量**: 全部大写加下划线 (`UPPER_CASE`)
- **私有属性/方法**: 前缀单下划线 (`_private`)
- **强私有属性/方法**: 前缀双下划线 (`__very_private`)

### 代码布局
- 使用 4 个空格作为缩进（不要使用 Tab）
- 每行最大长度为 79 个字符
- 二元运算符应换行到下一行的开头
- 在类和函数之间使用两个空行分隔

### 导入规范
- 每个导入应该独占一行
- 按照标准库、第三方库、本地应用/库的顺序分组
- 不要使用 `from module import *`

## 2. PEP 257 - 文档字符串约定

- 使用三引号编写文档字符串
- 模块级文档字符串应在模块开头
- 类和函数都应该有文档字符串
- 概述行应该独立成行

## 3. 类型提示 (Type Hints) - PEP 484

现代 Python 代码应该使用类型提示：

```python
from typing import List, Dict, Optional

def greet(name: str) -> str:
    return f"Hello, {name}!"

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

def find_user(user_id: int) -> Optional[str]:
    # 返回 str 或 None
    pass
```

## 4. PEP 572 - 赋值表达式 (海象操作符)

可以在条件表达式中赋值：
```python
if (n := len(a)) > 10:
    print(f"List is too long ({n} elements, expected <= 10)")
```

## 5. 现代工具和最佳实践

### 代码格式化工具
- **Black**: 自动格式化代码，强制统一风格
- **autopep8**: 自动修复 PEP 8 问题
- **YAPF**: Google 开发的格式化工具

### 代码检查工具
- **Flake8**: 检查代码风格和错误
- **pylint**: 提供详细的代码分析
- **mypy**: 静态类型检查
- **bandit**: 安全漏洞检测

### 依赖管理
- **Poetry**: 现代化的依赖管理和打包工具
- **Pipenv**: 结合 pip 和 virtualenv 的功能
- **requirements.txt**: 传统的依赖管理方式

## 6. 目录和命名规范

### 项目结构
```
project_name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
├── docs/
├── .gitignore
├── README.md
├── pyproject.toml
├── setup.py (如果需要)
└── LICENSE
```

### 目录命名规范
- 使用小写字母和下划线 (`snake_case`)
- 保持目录名简短且具有描述性
- 避免使用特殊字符和空格
- 使用复数形式表示集合（如 `models/`, `views/`, `utils/`）
- 版本相关目录使用前缀 `v` 加数字（如 `v1_0`, `v2_5`）

### 命名约定
- **变量和函数名**: 使用小写字母和下划线 (`snake_case`)
- **类名**: 使用驼峰命名法 (`CamelCase`)
- **常量**: 全部大写加下划线 (`UPPER_CASE`)
- **私有属性/方法**: 前缀单下划线 (`_private`)
- **强私有属性/方法**: 前缀双下划线 (`__very_private`)

### 模块结构
```python
"""Module docstring describing what this module does."""

import os  # 标准库
import sys

import requests  # 第三方库

from mypackage import mymodule  # 本地库

CONSTANT = "value"

class MyClass:
    """Class docstring."""
    
    def __init__(self):
        """Initialize the class."""
        pass

def my_function(arg1: str, arg2: int) -> bool:
    """Function docstring.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Description of return value
    """
    return True

if __name__ == "__main__":
    # 仅在直接运行此脚本时执行的代码
    pass
```

## 7. 异常处理规范

- 捕获具体的异常而不是通用的 `Exception`
- 使用 `finally` 或 `with` 语句确保资源清理
- 编写有意义的异常消息

## 8. 性能和可读性建议

- 避免不必要的全局变量
- 使用生成器表达式代替列表推导式（当只需要迭代一次时）
- 使用 `collections` 模块中的特殊数据结构
- 使用 `pathlib` 处理路径操作
- 遵循 DRY (Don't Repeat Yourself) 原则

## 9. 测试规范

- 遵循测试驱动开发 (TDD) 或行为驱动开发 (BDD)
- 使用 pytest 或 unittest 框架
- 测试覆盖率目标通常为 80%+
- 编写单元测试、集成测试和端到-end测试

## 10. 注释和文档规范

- 所有代码必须添加必要的注释，注释必须使用英文
- 使用 Sphinx 生成文档
- 遵循 reStructuredText 格式
- 为公共 API 提供详细文档
- 使用示例代码说明复杂概念

这些规范共同构成了现代 Python 开发的最佳实践，遵循这些规范可以提高代码的可读性、可维护性和协作效率。