# 招生智能体系统 - 静态报告

## 在线查看

舅舅可以通过这个链接在线查看招生线索分析报告：

> **将你的GitHub用户名替换下方链接后访问**
> `https://你的用户名.github.io/zhaosheng-report/`

## 部署到GitHub Pages（免费，永久在线）

### 步骤一：创建GitHub仓库

1. 打开 https://github.com/new
2. 仓库名填：`zhaosheng-report`
3. 选择 Public（公开）
4. 点击 Create repository

### 步骤二：上传代码

```bash
cd C:\Users\唐先生\Documents\招生agent系统\docs
git init
git add .
git commit -m "初始版本：招生线索分析报告"
git branch -M main
git remote add origin https://github.com/你的用户名/zhaosheng-report.git
git push -u origin main
```

### 步骤三：开启GitHub Pages

1. 打开 https://github.com/你的用户名/zhaosheng-report/settings/pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 "main"，文件夹选择 "/ (root)"
4. 点击 Save
5. 等1-2分钟，访问 `https://你的用户名.github.io/zhaosheng-report/`

## 更新数据

当有新的咨询数据时，重新运行系统生成报告，然后：
```bash
cd C:\Users\唐先生\Documents\招生agent系统\docs
git add .
git commit -m "更新报告数据"
git push
```
