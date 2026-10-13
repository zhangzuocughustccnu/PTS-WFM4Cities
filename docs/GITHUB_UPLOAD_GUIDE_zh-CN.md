# GitHub上传与3.0.0发布指南

## 1. 本次更新的性质

当前GitHub仓库只有两个独立PY文件。新版不是在旁边补几个说明文件，而是
将其升级为标准的Python项目。因此，上传时应整体替换仓库根目录内容，不能
只把新文件追加进去，否则旧的 `water-flooding model.py` 会继续与新版
入口并存。

## 2. 推荐方式：GitHub Desktop

1. 用GitHub Desktop克隆
   `https://github.com/zhangzuocughustccnu/WFM4Cities`。
2. 新建分支 `release/3.0.0`。
3. 将本压缩包根目录内的全部文件和文件夹复制到本地仓库根目录。
4. 删除仓库原有的 `water-flooding model.py`。原始
   `WFM4Cities.py` 已完整保存在 `legacy/WFM4Cities_2.6_original.py`，
   新根目录中的同名文件是兼容启动器。
5. 确认隐藏目录 `.github` 也已复制。
6. 在GitHub Desktop中检查变更，提交信息建议为：
   `Prepare WFM4Cities 3.0.0`。
7. 推送分支，在GitHub上创建Pull Request。
8. 等待CI全部通过后合并到 `main`。

## 3. 命令行方式

在已经克隆的仓库根目录执行：

    git checkout -b release/3.0.0
    git status
    git add --all
    git status
    git commit -m "Prepare WFM4Cities 3.0.0"
    git push --set-upstream origin release/3.0.0

`git add --all` 很重要，因为它会同时记录新增文件、修改文件和旧重复脚本的
删除。提交前务必通过 `git status` 确认没有个人数据、临时输出或密钥。

## 4. GitHub网页上传的注意事项

网页拖放不适合这次结构化更新，因为容易漏掉 `.github` 隐藏目录，也不会
自动删除旧文件。如果必须使用网页：

1. 分批保持原目录结构上传；
2. 单独确认 `.github/workflows`、`.github/ISSUE_TEMPLATE` 已存在；
3. 手工删除旧的 `water-flooding model.py`；
4. 打开Actions页确认CI能够识别并运行。

## 5. 本地核验

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"
    ruff check .
    pytest
    python -m build
    python -m twine check dist/*

macOS/Linux将激活命令替换为 `source .venv/bin/activate`。

## 6. PyPI发布

PyPI上已有 `WFM4Cities 2.6`，因此新版本必须使用更高版本号；本项目已经
统一设为 `3.0.0`。当前PyPI页面显示维护者为 `JIANGYUKUN`。正式发布前，
该维护者需要完成以下任一操作：

- 在PyPI项目中为本GitHub仓库配置Trusted Publisher；或
- 将实际负责发布的PyPI账号加入项目维护者。

建议采用Trusted Publishing：

1. PyPI项目名：`WFM4Cities`；
2. GitHub owner：`zhangzuocughustccnu`；
3. repository：`WFM4Cities`；
4. workflow：`publish.yml`；
5. environment：`pypi`。

随后在GitHub仓库Settings → Environments中新建 `pypi`，并设置人工批准。
发布GitHub Release `v3.0.0` 后，工作流会自动构建并上传wheel和源码包。

## 7. 永久归档

建议先将GitHub仓库连接Zenodo，再发布 `v3.0.0`。Zenodo归档成功后，把
真实DOI补入：

- `CITATION.cff`；
- README中英文版；
- WFM4Cities用户手册；
- 论文的数据、材料与代码可用性声明。

在Zenodo实际生成以前，不要填写猜测或占位DOI。
