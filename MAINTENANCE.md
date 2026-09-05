# 个人主页维护

这个公开仓库与 GitHub 用户名同名，因此根目录 `README.md` 会显示在个人主页。
无需 GitHub Pages、前端框架或部署服务。

## 内容与样式

- `README.md`：介绍、项目链接、卡片布局。
- `scripts/update_stats.py`：从公开 GitHub API 获取数据，生成支持明暗主题的 SVG。
- `assets/`：已提交的统计卡片，GitHub 直接加载，不依赖外部统计卡片服务。
- `.github/workflows/update-stats.yml`：每日约 UTC 04:23 更新，也支持手动触发。

介绍根据当前公开项目整理；修改 README 即可更换语言或措辞。
Follow 徽章由 Shields.io 提供，点击打开关注者页面，并不会自动关注。

## 手动更新

需要 Python 3 和已登录的 GitHub CLI，无第三方 Python 依赖：

```sh
python3 scripts/update_stats.py
```

本地运行使用现有 gh 登录态。Actions 使用自动提供的 `GITHUB_TOKEN`，无需添加个人令牌。
请求失败时任务报错，保留上次提交的卡片。仅扫描公开、非 fork 仓库，不读取私有仓库。
语言百分比按 GitHub Languages API 的代码字节数计算，排除本主页仓库；仅展示前五种，
分母仍包含全部语言，因此显示比例不一定合计为 100%。Stars 和 forks 汇总自公开原创仓库。

## 自动更新注意事项

GitHub 定时任务可能延迟；公开仓库长期无活动时定时工作流可能被暂停。
可进入 Actions → Update profile stats → Run workflow 手动更新或恢复。
如组织策略或分支保护禁止机器人推送，需相应调整策略；不要将令牌写进仓库。

## 提交修改

```sh
git add README.md
git commit -m "docs: update profile"
git push
```
