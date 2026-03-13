"""
数据集下载脚本
列出常用代码缺陷检测数据集的下载地址
"""

DATASETS_INFO = """
================================================================================
                    代码缺陷检测数据集资源汇总
================================================================================

一、CodeXGLUE 数据集
--------------------------------------------------------------------------------
地址: https://github.com/microsoft/CodeXGLUE
下载: 
  git clone https://github.com/microsoft/CodeXGLUE.git
  cd CodeXGLUE
  # 进入 Defect-detection 目录

相关论文: https://arxiv.org/abs/2102.04664

二、Devign 数据集 (来自CodeXGLUE)
--------------------------------------------------------------------------------
描述: C代码漏洞检测数据集，包含多种漏洞类型
地址: https://github.com/ZhouJiahua/DeepLearningVulDetection
     或通过CodeXGLUE获取

漏洞类型: 
  - Resource leak (资源泄漏)
  - Use-after-free (使用已释放内存)
  - DoS attack (拒绝服务攻击)
  - Buffer overflow (缓冲区溢出)

三、HuggingFace 代码数据集
--------------------------------------------------------------------------------
1. bigcode/the-stack
   地址: https://huggingface.co/datasets/bigcode/the-stack
   描述: 最大的开源代码数据集，包含多种语言
   下载: 
     from datasets import load_dataset
     ds = load_dataset("bigcode/the-stack", split="train[:1000]")

2. code_search_net
   地址: https://huggingface.co/datasets/code_search_net
   描述: 代码搜索网络数据集

3. github Jaffathon
   地址: https://huggingface.co/datasets/Jaffathon/github_vulnerabilities
   描述: GitHub漏洞数据集

四、SARD (Software Assurance Reference Dataset)
--------------------------------------------------------------------------------
地址: https://samate.nist.gov/SARD/
描述: NIST软件保证参考数据集
特点: 包含大量真实世界缺陷和修复

五、Py150 数据集
--------------------------------------------------------------------------------
地址: https://huggingface.co/datasets/microsoft/py150
描述: 150K Python代码片段

六、BigFix 数据集
--------------------------------------------------------------------------------
地址: https://github.com/xing-hu/BigFix
描述: 大规模C代码缺陷修复数据集
样本数: 40,000+ 缺陷案例

七、GitHub API 获取PR评论
--------------------------------------------------------------------------------
地址: https://docs.github.com/en/rest
使用方式:
   # 需要GitHub Token
   curl -H "Authorization: token YOUR_TOKEN" \\
        https://api.github.com/repos/OWNER/REPO/pulls/comments

================================================================================
"""

SAMPLE_DOWNLOAD_CODE = '''
# ========================================
# 使用HuggingFace datasets库下载示例
# ========================================

# 安装依赖
pip install datasets

# 下载代码数据集
from datasets import load_dataset

# 下载bigcode/the-stack (Python子集)
dataset = load_dataset(
    "bigcode/the-stack",
    language="Python",
    split="train[:10000]"  # 下载前10000条
)

# 查看数据
print(dataset)
print(dataset[0])

# 下载代码搜索数据集
code_search = load_dataset("code_search_net", "python")
print(code_search)
'''

def print_datasets_info():
    """打印数据集信息"""
    print(DATASETS_INFO)
    print("\n" + "="*80)
    print("快速下载示例代码:")
    print("="*80)
    print(SAMPLE_DOWNLOAD_CODE)


def download_sample_data():
    """下载示例数据（需要网络连接）"""
    try:
        from datasets import load_dataset
        
        print("正在从HuggingFace下载示例数据...")
        
        # 尝试下载小样本
        try:
            dataset = load_dataset(
                "bigcode/the-stack",
                language="Python",
                split="train[:100]",
                trust_remote_code=True
            )
            print(f"成功下载 {len(dataset)} 条Python代码")
            return dataset
        except Exception as e:
            print(f"bigcode下载失败: {e}")
        
        return None
        
    except ImportError:
        print("请先安装datasets库: pip install datasets")
        return None
    except Exception as e:
        print(f"下载失败: {e}")
        return None


if __name__ == "__main__":
    print_datasets_info()
    
    print("\n" + "="*80)
    print("尝试下载示例数据...")
    print("="*80)
    
    dataset = download_sample_data()
    if dataset:
        print("\n示例数据下载成功！")
    else:
        print("\n示例数据下载失败，请检查网络或手动下载")
