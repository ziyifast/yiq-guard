# 贡献指南

感谢你对 yiQGuard 的关注！欢迎以任何形式参与贡献。

## 如何贡献

### 报告 Bug

1. 确认你使用的是最新版本
2. 在 [Issues](https://github.com/ziyi/yiq-guard/issues) 中搜索是否已有相同问题
3. 创建新 Issue，包含：
   - macOS 版本
   - Python 版本
   - 复现步骤
   - 期望行为 vs 实际行为

### 提交功能建议

在 Issues 中创建 Feature Request，描述：
- 你想解决什么问题
- 你设想的解决方案
- 可能的替代方案

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 编写代码并添加测试
4. 确保所有测试通过：`python -m pytest tests/ -v`
5. 提交：`git commit -m "feat: add your feature"`
6. 推送：`git push origin feature/your-feature`
7. 创建 Pull Request

## 开发环境搭建

```bash
git clone https://github.com/ziyi/yiq-guard.git
cd yiq-guard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest
```

## 代码规范

- 使用 4 空格缩进
- 函数/方法添加 docstring
- 变量命名使用 snake_case
- 类命名使用 PascalCase
- 提交信息使用 [Conventional Commits](https://www.conventionalcommits.org/)：
  - `feat:` 新功能
  - `fix:` 修复 Bug
  - `docs:` 文档改动
  - `refactor:` 重构
  - `test:` 测试相关
  - `chore:` 杂项

## 测试要求

- 新功能必须附带测试
- 测试可在 Linux/CI 环境运行（使用 `tests/mocks/macos_mocks.py`）
- 运行全部测试：`python -m pytest tests/ -v`

## 项目结构约定

- 新的保护模式放在 `yiqguard/modes/`
- UI 组件放在 `yiqguard/ui/`
- 测试文件命名为 `test_<module>.py`
- Mock 对象放在 `tests/mocks/`

## License

贡献的代码将采用与本项目相同的 [MIT License](LICENSE)。
