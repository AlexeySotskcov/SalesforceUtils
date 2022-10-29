from tkinter import *
from tkinter import ttk, scrolledtext, filedialog, messagebox

from functools import partial
import os

import permreader

win = Tk()
win.title('Access provider')
win.geometry('620x340')
win.resizable(False, False)
file_name = Entry(win, font=("Calibri 12"), state='disabled')

label_fileType = Label(win)
label_fileType.config(text='chosen file type: ')

label_chosenFileType = Label(win)
label_chosenFileType.config(text='', font=("Arial", 14))

label_result = Label(win)
label_result.config(text='File Name: ')

tab_parent = ttk.Notebook(win)
tab1 = ttk.Frame(tab_parent)

tab_parent.add(tab1, text="fieldPermissions")
readable_var = BooleanVar()
editable_var = BooleanVar()
remove_var = BooleanVar()

filepath_var = StringVar()
filepath_var_list = []

message = 'Test.Test_Field__c'


text_box = scrolledtext.ScrolledText(tab1, wrap=WORD, width=45, height=7, font=("Times New Roman", 15))
text_box.grid(row=0, column=0, columnspan=2, rowspan=20, padx=5, pady=5, sticky='w')



def select_file(filepath_var):
    type_var = StringVar()

    file_name.config(state='normal')
    file_name.delete(0, END)
    filetypes = (
        ('permission set', '*.permissionset-meta.xml'),
        ('profile', '*.profile-meta.xml')
    )
    filename = filedialog.askopenfilename(
        title='Open file',
        initialdir='/',
        filetypes=filetypes,
        typevariable=type_var
    )

    label_chosenFileType.config(text=type_var.get())
    fName = os.path.split(filename)[1].split('.')[0]

    filepath_var.set(filename)

    file_name.insert(END, fName)
    file_name.config(state=DISABLED)


def select_files(filepath_var_list):
    file_name.config(state='normal')
    file_name.delete(0, END)
    type_var = StringVar()

    filetypes = (
        ('permission sets', '*.permissionset-meta.xml'),
        ('profiles', '*.profile-meta.xml')
    )

    filenames = filedialog.askopenfilenames(
        title='Open files',
        initialdir='/',
        filetypes=filetypes,
        typevariable=type_var
    )


    for filename in filenames:
        filepath_var_list.append(filename)

    fName = ''

    for filename in filepath_var_list:
        fName += os.path.split(filename)[1].split('.')[0] + '; '

    file_name.insert(END, fName)
    file_name.config(state=DISABLED)
    label_chosenFileType.config(text=type_var.get())


def update_editable_checkbox(isReadable):
    isReadable.set(1)
    return


def update_readable_checkbox(isReadable, isEditable):
    if (isEditable.get() == 1):
        isReadable.set(1)

    return


def update_remove_checkbox(isRemove, isReadableCheckbox, isEditableCheckbox):
    if (isRemove.get() == 1):
        isReadableCheckbox.configure(state='disabled')
        isEditableCheckbox.configure(state='disabled')
    else:
        isReadableCheckbox.configure(state='normal')
        isEditableCheckbox.configure(state='normal')
    return


def process_file(filepath, isReadable, isEditable, isRemove, text_box):
    fPath = ''
    if (type(filepath) is str):
        fPath = filepath
    else:
        fPath = filepath.get()

    if not fPath:
        messagebox.showerror(title='Select file', message='There no file selected')
        return

    fields = text_box.get("1.0", END)
    is_Editable = isEditable.get()
    is_Readable = isReadable.get()
    is_Remove = isRemove.get()
    fieldsForUpdate = getFieldsList(fields)
    permreader.main(fPath, is_Editable, is_Readable, is_Remove, fieldsForUpdate)
    return



def process_files(filespath_list, isReadable, isEditable, isRemove, text_box):
    if not filespath_list:
        messagebox.showerror(title='Select file', message='There no file selected')
        return

    for filepath in filespath_list:
        process_file(filepath, isReadable, isEditable, isRemove, text_box)

    messagebox.showinfo(title='Done', message='Files Processed')



def getFieldsList(fildsList):
    return fildsList.replace(" ", "").replace("\n", "").split(";")


def close_app():
    quit()



def normalize_file(filepath):
    fPath = ''
    if (type(filepath) is str):
        fPath = filepath
    else:
        fPath = filepath.get()

    if not fPath:
        messagebox.showerror(title='Select file', message='There is no file selected')
        return

    permreader.normalize(fPath)
    return


selectFiles = partial(select_files, filepath_var_list)

updateEditableCheckbox = partial(update_editable_checkbox, readable_var)
updateReadableCheckbox = partial(update_readable_checkbox, readable_var, editable_var)


processFiles = partial(process_files, filepath_var_list, readable_var, editable_var, remove_var, text_box)

open_few_btn = Button(win, text="Choose files", command=selectFiles)

is_readable = Checkbutton(tab1, text='Readable', variable=readable_var, onvalue=1, offvalue=0,
                             command=updateReadableCheckbox)
is_editable = Checkbutton(tab1, text='Editable', variable=editable_var, onvalue=1, offvalue=0,
                             command=updateReadableCheckbox)

updateRemoveCheckbox = partial(update_remove_checkbox, remove_var, is_readable, is_editable)
is_remove = Checkbutton(tab1, text='Remove Fields', variable=remove_var, onvalue=1, offvalue=0,
                           command=updateRemoveCheckbox)

normalizeFile = partial(normalize_file, filepath_var)

process_multi_btn = Button(win, text="Process files", command=processFiles)

normalize_btn = Button(win, text="Normalize", command=normalizeFile)
cancel_btn = Button(win, text="Close App", command=close_app)

label_fileType.grid(row=0, column=0, sticky='w', padx=20)
label_chosenFileType.grid(row=0, column=1, columnspan=2)

label_result.grid(row=1, column=0, sticky='w', padx=20)
file_name.grid(row=1, column=1, sticky='nsew')

open_few_btn.grid(row=1, column=2, sticky='n', padx=20)

is_readable.grid(row=0, column=2, sticky='w')
is_editable.grid(row=1, column=2, sticky='w')
is_remove.grid(row=2, column=2, sticky='w')

normalize_btn.grid(row=4, column=0, sticky='nsew', pady=(20, 0), padx=20)

process_multi_btn.grid(row=4, column=1, sticky='nsew', pady=(20, 0), padx=20)
cancel_btn.grid(row=4, column=2, sticky='nsew', pady=(20, 0), padx=20)

tab_parent.grid(row=2, column=0, columnspan=3, padx=(20, 0), pady=(20, 0), sticky='nsew')

text_box.insert('end', message)

win.mainloop()
