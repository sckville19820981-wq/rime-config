# Rime 配置

鼠鬚管（Squirrel）+ 雾凇拼音，横排候选、毛玻璃、拆字优化。

只跟踪自定义文件，词库和编译产物靠 plum 重装。

## 跟踪了什么

| 文件 | 作用 |
|---|---|
| `squirrel.custom.yaml` | 外观：配色、字体、排版 |
| `default.custom.yaml` | 通用快捷键 |
| `rime_ice.custom.yaml` | 方案行为：拆字前缀、学习、注音、滤镜 |
| `lua/radical_sort_filter.lua` | 拆字候选重排（常用字提前） |
| `lua/char_freq.lua` | 单字词频表，上面那个滤镜用 |

## 换新电脑

```bash
# 1. 装输入法和字体
brew install --cask squirrel font-plangothic

# 2. 装 plum
git clone https://github.com/rime/plum.git ~/plum

# 3. 装雾凇拼音 + 拆字带声调注音词典
cd ~/plum
bash rime-install iDvel/rime-ice
bash rime-install mirtlecn/rime-radical-pinyin:extra

# 4. 拉本仓库覆盖配置
cd ~/Library/Rime && git init && git remote add origin <仓库地址>
git fetch origin && git checkout -f main
```

然后系统设置 → 键盘 → 输入方式 → 加「鼠鬚管」，
再点菜单栏图标「重新部署」。

## 快捷键

| 键 | 作用 |
|---|---|
| `Ctrl+Shift+F` | 简繁切换 |
| `Ctrl+Shift+P` | 中英标点 |
| `Ctrl+Shift+E` | Emoji 开关 |
| `F4` | 方案选单 |
| `Ctrl+Delete` | 删除/降权选中的候选词 |
| `` ` `` | 辅码筛选，如 `hui`+`` ` ``+`cao` → 荟 |
| `uu` + 部件拼音 | 拆字，如 `uuririri` → 晶 |

## 个人词库怎么带

`*.userdb/` 没有跟踪 —— 它是 LevelDB，跟 `installation_id` 绑定，
跨机器直接拷目录可能不被识别。正规做法：

1. 旧机器：菜单栏鼠鬚管图标 → 「同步用户资料」，
   会导出纯文本到 `~/Library/Rime/sync/<installation_id>/`
2. 把那个目录拷到新机器的 `~/Library/Rime/sync/` 下
3. 新机器再点一次「同步用户资料」，会自动合并

文本格式跨机器通用，也能直接看内容。

## 更新词库

```bash
cd ~/plum && bash rime-install iDvel/rime-ice
```

跑完重新部署。`*.custom.yaml` 是补丁机制，不会被覆盖。

## 改完配置记得

菜单栏鼠鬚管图标 → **重新部署**，否则不生效。
