" 开启文件类型检查，并且载入与该类型对应的缩进规则。比如，如果编辑的是.py文件，Vim 就是会找 Python 的缩进规则~/.vim/indent/python.vim
filetype plugin indent on

" c语言，C++，Python,JavaScript用4格缩进，其他用两格
"autocmd FileType c,cpp,py,javascript set shiftwidth=4 tabstop=4 softtabstop=4

set tabstop=4 softtabstop=4 shiftwidth=4
autocmd FileType HTML,markdown set shiftwidth=2 tabstop=2 softtabstop=2


" 由于 Tab 键在不同的编辑器缩进不一致，该设置自动将 Tab 转为空格。
set expandtab

" 按下回车键后，下一行的缩进会自动跟上一行的缩进保持一致。
set autoindent
set smartindent

" show line number
set number

" 显示光标所在的当前行的行号，其他行都为相对于该行的相对行号。
"set relativenumber

" 光标所在的当前行高亮。
set cursorline

" 在状态栏显示光标的当前位置（位于哪一行哪一列）。
set  ruler

" 水平滚动时，光标距离行首或行尾的位置（单位：字符）。
set sidescrolloff=15

" 垂直滚动时，光标距离顶部/底部的位置（单位：行）。
set scrolloff=5

" 不与 Vi 兼容（采用 Vim 自己的操作命令）
set nocompatible

" 打开语法高亮。自动识别代码，使用多种颜色显示。
" Not work @ 2020-05-02
"syntax on

" 在底部显示，当前处于命令模式还是插入模式。
set showmode

" 命令模式下，在底部显示，当前键入的指令。比如，键入的指令是2y3d，那么底部就会显示2y3，当键入d的时候，操作完成，显示消失。
set showcmd

" 支持使用鼠标。
" Not work @ 2020-05-02
"set mouse=a

" 使用 utf-8 编码。
set encoding=utf-8

" 启用256色。
"set t_Co=256

" 是否显示状态栏。0 表示不显示，1 表示只在多窗口时显示，2 表示显示。
set laststatus=2

" 第80列显示红色竖线
highlight StatusLine cterm=bold ctermfg=yellow ctermbg=blue
"let &colorcolumn="80"  # Not work@ubuntu19.10 2020-05-02
res +80
vertical res +20


" / Search
" 光标遇到圆括号、方括号、大括号时，自动高亮对应的另一个圆括号、方括号和大括号。
set showmatch
" 搜索时，高亮显示匹配结果。
set hlsearch
" 输入搜索模式时，每输入一个字符，就自动跳到第一个匹配的结果。
set incsearch
" 搜索时忽略大小写。
set ignorecase
" 如果同时打开了ignorecase，那么对于只有一个大写字母的搜索词，将大小写敏感；其他情况都是大小写不敏感。比如，搜索Test时，将不匹配test；搜索test时，将匹配Test。
set smartcase


" Uncomment the following to have Vim jump to the last position when
" reopening a file
if has("autocmd")
    au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
    " for simplicity, "  au BufReadPost * exe "normal! g`\"", is Okay.
endif


"" allows cursor change in tmux mode
"if exists('$TMUX')
"    let &t_SI = "\<Esc>Ptmux;\<Esc>\<Esc>]50;CursorShape=1\x7\<Esc>\\"
"    let &t_EI = "\<Esc>Ptmux;\<Esc>\<Esc>]50;CursorShape=0\x7\<Esc>\\"
"else
"    let &t_SI = "\<Esc>]50;CursorShape=1\x7"
"    let &t_EI = "\<Esc>]50;CursorShape=0\x7"
"endif
