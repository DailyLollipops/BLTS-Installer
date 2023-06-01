import tkinter as tk
import tkinter.ttk as ttk
import os
import subprocess
import shutil
import psutil
import pymysql
import time
from tkinter import messagebox
from typing import Union
from zipfile import ZipFile
from threading import Thread

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ZIP_NAME = 'BLTS.zip'
COMPRESSED_CODES = fr'{DIRECTORY}/{ZIP_NAME}'
SHORTCUT = fr'{DIRECTORY}/BLTS.url'
LARAGON_PATH = r'C:/laragon'
LARAGON_PROJECT_PATH = fr'{LARAGON_PATH}/www'
WORKING_DIRECTORY = fr'{LARAGON_PROJECT_PATH}/BLTS'
DESKTOP = os.path.join (os.path.join (os.environ['USERPROFILE']), 'Desktop')
DESKTOP_ONEDRIVE = os.path.join(os.path.join(os.path.join (os.environ ['USERPROFILE']), 'OneDrive'), 'Desktop')
PHP = fr'"{LARAGON_PATH}\bin\php\php-8.1.10-Win32-vs16-x64\php.exe"'
Widget = Union[tk.Widget, ttk.Widget]

class RootWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('500x600')
        self.resizable(False, False)

        img = tk.PhotoImage(file='hero.png')
        hero = tk.Label(self, image = img)
        hero.image = img
        hero.place(x = 90, y = 25)

        self.uninstall_button = tk.Button(self, text = 'Uninstall', height = 2, width = 20, font = ('Calibri', 14, 'bold'), cursor = 'hand2', command = self.uninstall)
        self.uninstall_tooltip = ToolTip(self)
        self.uninstall_tooltip.bind(self.uninstall_button, 'Uninstall BLTS.\nAll files and data will be removed permanently')

        self.install_button = tk.Button(self, text = 'Install', height = 2, width = 20, font = ('Calibri', 14, 'bold'), cursor = 'hand2', command = self.install)
        self.install_tooltip = ToolTip(self)
        self.install_tooltip.bind(self.install_button, 'Install BLTS. \n Requires Laragon to be installed first.')

        self.create_migration_button = tk.Button(self, text = 'Create Migration Data', height = 2, width = 20, font = ('Calibri', 14), cursor = 'hand2', command = self.create_migration)
        self.create_migration_button.place(x = 160, y = 300)
        self.create_migration_tooltip = ToolTip(self)

        self.migrate_button = tk.Button(self, text = 'Migrate Data', height = 2, width = 20, font = ('Calibri', 14), cursor = 'hand2')
        self.migrate_button.place(x = 160, y = 390)
        self.migrate_tooltip = ToolTip(self)

        footer_text = 'BLTS is a project completed during the 2023 DILG Internship\nin collaboration with the Computer Engineering on-the-job trainees\nfrom the Marinduque State College (MSC)'
        footer = tk.Label(self, height = 5, width = 85, font = ('Calibri', 9), bg = '#425B71', fg = 'white', padx = 2, pady = 1, text = footer_text)
        footer.place(x = 0, y = 525)
    
        if os.path.exists(WORKING_DIRECTORY):
            self.uninstall_button.place(x = 160, y = 210)
            self.create_migration_tooltip.bind(self.create_migration_button, 'Generate Migration Data.\nUsed for migrated current data to another device')
            self.migrate_tooltip.bind(self.migrate_button, 'Migrate selected data.\nMigration will delete current BLTS data.')
        else:
            self.install_button.place(x = 160, y = 210)
            self.create_migration_button['state'] = 'disabled'
            self.create_migration_tooltip.bind(self.create_migration_button, 'BLTS is not installed.\nPlease install first before using this feature')
            self.migrate_button['state'] = 'disabled'
            self.migrate_tooltip.bind(self.migrate_button, 'BLTS is not installed.\nPlease install first before using this feature')


    def delete_existing_database(self):
        host = '127.0.0.1'
        user = 'root'
        password = ''
        charset = 'utf8mb4'
        cursor = pymysql.cursors.DictCursor

        try:
            connection = pymysql.connect(
                host = host,
                user = user,
                password = password,
                charset = charset,
                cursorclass = cursor
            )
        except pymysql.err.OperationalError:
            process = subprocess.Popen(['C:\laragon\laragon','reload','apache'])
            try:
                process.wait(10)
            except subprocess.TimeoutExpired:
                self.progress.set('Apache reloaded successfully')
                connection = pymysql.connect(
                    host = host,
                    user = user,
                    password = password,
                    charset = charset,
                    cursorclass = cursor
                )

        try:
            db_cursor = connection.cursor()
            sql = "DROP DATABASE IF EXISTS blts;"
            db_cursor.execute(sql)
        except Exception as e:
            print("Exeception occured:{}".format(e))
        finally:
            connection.close()

    def install(self):
        install_window = InstallWindow(self)

    def uninstall(self):
        unistall_window = UninstallWindow(self)

    def create_migration(self):
        create_migration_window = CreateMigrationWindow(self)

    def update(self):
        if os.path.exists(WORKING_DIRECTORY):
            self.install_button.place_forget()
            self.uninstall_button.place(x = 160, y = 210)
            self.create_migration_button['state'] = 'normal'
            self.create_migration_tooltip.bind(self.create_migration_button, 'Generate Migration Data.\nUsed for migrated current data to another device')
            self.migrate_button['state'] = 'normal'
            self.migrate_tooltip.bind(self.migrate_button, 'Migrate selected data.\nMigration will delete current BLTS data.')
        else:
            self.uninstall_button.place_forget()
            self.install_button.place(x = 160, y = 210)
            self.create_migration_button['state'] = 'disabled'
            self.create_migration_tooltip.bind(self.create_migration_button, 'BLTS is not installed.\nPlease install first before using this feature')
            self.migrate_button['state'] = 'disabled'
            self.migrate_tooltip.bind(self.migrate_button, 'BLTS is not installed.\nPlease install first before using this feature')
        

class InstallWindow(tk.Toplevel):
    def __init__(self, root:RootWindow):
        tk.Toplevel.__init__(self, root)
        self.root = root
        self.geometry('400x100')
        self.resizable(False, False)
        self.grab_set()

        self.progress = tk.StringVar()
        self.progress.set('Initializing...')
        self.progressbar_label = tk.Label(self, height = 3, padx = 1, justify = tk.LEFT, font = ('Calibri', 10), textvariable = self.progress)
        self.progressbar_label.place(x = 30, y = 2.5)
        self.progressbar = ttk.Progressbar(self, orient = 'horizontal', length = 340, mode = 'determinate')
        self.progressbar.place(x = 30, y = 40)

        install_thread = Thread(target = self.install)
        self.after(3000, install_thread.start)

    def install(self):
        copy_success = False
        self.progress.set('Checking if Laragon is installed...')
        if os.path.exists(LARAGON_PATH):
            self.progress.set('Laragon found and verified')
            if(os.path.isfile(COMPRESSED_CODES)):
                self.progress.set('BLTS compressed source codes found!')
                if(os.path.isfile(fr'{LARAGON_PROJECT_PATH}/BLTS')):
                    self.progress.set('BLTS Application already exist in Laragon directory...')
                    self.progress.set('Removing existing BLTS Application')
                    shutil.rmtree(fr'{LARAGON_PROJECT_PATH}/BLTS')
                    self.progress.set('Existing BLTS Application removed...')
                self.progressbar['value'] = 10
                self.progress.set('Moving project source codes to Laragon directory')
                shutil.copy(COMPRESSED_CODES, LARAGON_PROJECT_PATH)
                self.progressbar['value'] = 50
                with ZipFile(fr'{LARAGON_PROJECT_PATH}/{ZIP_NAME}', 'r') as zip:
                    self.progress.set('Extracting application source codes to Laragon')
                    zip.extractall(LARAGON_PROJECT_PATH)
                    self.progress.set('Source codes successfully extracted!')
                    self.progressbar['value'] = 80
                os.remove(fr'{LARAGON_PROJECT_PATH}/{ZIP_NAME}')
                self.progress.set('Compressed source codes removed')
                copy_success = True
            else:
                self.progress.set('BLTS compressed source codes not found!')
                messagebox.showerror('Codes not found', 'BLTS compressed source codes not found!')
        else:
            self.progress.set('Laragon not found. Please install the full version first at https://laragon.org/download/')
            messagebox.showerror('Laragon not found', 'Laragon not found. Please install the full version first at https://laragon.org/download/')

        if(copy_success):
            self.progress.set('Project moved to host directory')
            self.progress.set('Please wait for the first-time setup to complete')
            self.root.delete_existing_database()
            self.progressbar['value'] = 90
            os.chdir(WORKING_DIRECTORY)
            os.system(f'{PHP} artisan storage:link')
            os.system(f'{PHP} artisan migrate --seed --force')
            self.progressbar['value'] = 95
            shutil.copy(fr'{SHORTCUT}', DESKTOP)
            shutil.copy(fr'{SHORTCUT}', DESKTOP_ONEDRIVE)
            self.progress.set('Shortcut created on desktop!')
            self.progress.set('Reloading apache...')
            for process in psutil.process_iter():
                if process.name() == 'laragon.exe':
                    process.kill()
                    time.sleep(3)
            process = subprocess.Popen(['C:\laragon\laragon','reload','apache'])
            try:
                process.wait(10)
            except subprocess.TimeoutExpired:
                self.progress.set('Apache reloaded successfully')
            self.progressbar['value'] = 100
            self.progress.set('Installation Success!')
            messagebox.showinfo('Success', 'Installation Success!')
        self.root.update()
        self.destroy()


class UninstallWindow(tk.Toplevel):
    def __init__(self, root:RootWindow):
        tk.Toplevel.__init__(self, root)
        self.root = root
        self.geometry('400x100')
        self.resizable(False, False)
        self.grab_set()

        self.progress = tk.StringVar()
        self.progress.set('Initializing...')
        self.progressbar_label = tk.Label(self, height = 3, padx = 1, justify = tk.LEFT, font = ('Calibri', 10), textvariable = self.progress)
        self.progressbar_label.place(x = 30, y = 2.5)
        self.progressbar = ttk.Progressbar(self, orient = 'horizontal', length = 340, mode = 'determinate')
        self.progressbar.place(x = 30, y = 40)

        uninstall_thread = Thread(target = self.uninstall)
        self.after(3000, uninstall_thread.start)

    def uninstall(self):
        self.progress.set('Stopping Laragon...')
        for process in psutil.process_iter():
            if process.name() == 'laragon.exe':
                process.kill()
                time.sleep(3)
        self.progress.set('Deleting main application...')
        try:
            shutil.rmtree(WORKING_DIRECTORY)
        except Exception as e:
            print(e)
            os.removedirs(WORKING_DIRECTORY)
        self.progressbar['value'] = 70
        self.progress.set('Deleting database...')
        self.root.delete_existing_database()
        self.progressbar['value'] = 80
        self.progress.set('Removing desktop shortcut...')
        try:
            os.remove(fr'{DESKTOP}/BLTS.url')
        except:
            pass
        try:
            os.remove(fr'{DESKTOP_ONEDRIVE}/BLTS.url')
        except:
            pass
        self.progressbar['value'] = 90
        self.progress.set('Reloading Apache...')
        process = subprocess.Popen(['C:\laragon\laragon','reload','apache'])
        try:
            process.wait(10)
        except subprocess.TimeoutExpired:
            self.progress.set('Apache reloaded successfully')
        self.progressbar['value'] = 100
        messagebox.showinfo('Uninstall Success', 'BLTS successfully uninstalled!')
        self.root.update()
        self.destroy()


class CreateMigrationWindow(tk.Toplevel):
    def __init__(self, root:RootWindow):
        tk.Toplevel.__init__(self, root)
        self.root = root
        self.geometry('400x100')
        self.resizable(False, False)
        self.grab_set()

        self.progress = tk.StringVar()
        self.progress.set('Initializing...')
        self.progressbar_label = tk.Label(self, height = 3, padx = 1, justify = tk.LEFT, font = ('Calibri', 10), textvariable = self.progress)
        self.progressbar_label.place(x = 30, y = 2.5)
        self.progressbar = ttk.Progressbar(self, orient = 'horizontal', length = 340, mode = 'determinate')
        self.progressbar.place(x = 30, y = 40)

        create_migration_thread = Thread(target = self.create_migrate)
        self.after(1000, create_migration_thread.start)

    def create_migrate(self):
        path = askdirectory()
        if len(list(path)) <= 0:
            self.destroy()
            return
        self.progress.set('Exporting data...')
        shutil.copytree(fr'{WORKING_DIRECTORY}/storage/app/public/Documents', fr'{os.getcwd()}\BLTS\BLTS\Documents')
        shutil.copytree(fr'{WORKING_DIRECTORY}/storage/app/public/Profile', fr'{os.getcwd()}\BLTS\BLTS\Profile')
        shutil.copytree(fr'{WORKING_DIRECTORY}/storage/app/public/Reports', fr'{os.getcwd()}\BLTS\BLTS\Reports')                                                                                
        self.progress.set('Exporting database...')
        os.system(fr'C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysqldump -u root blts > BLTS\BLTS\blts.sql')        
        self.progress.set('Creating archive...')
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d-%H-%M-%S')
        shutil.make_archive(f'BLTS-data-{formatted_time}','zip', fr'{os.getcwd()}\BLTS')
        shutil.copy(fr'{os.getcwd()}\BLTS-data-{formatted_time}.zip', path)
        self.progress.set('Removing temp files...')
        shutil.rmtree(fr'{os.getcwd()}\BLTS')
        os.remove(fr'{os.getcwd()}\BLTS-data-{formatted_time}.zip')
        messagebox.showinfo('Success', 'Migration data successfull created!')
        self.destroy()

class ToolTip(tk.Toplevel):
    FADE_INC:float = .07
    FADE_MS :int   = 20
    
    def __init__(self, master, **kwargs):
        tk.Toplevel.__init__(self, master)
        self.attributes('-alpha', 0, '-topmost', True)
        self.overrideredirect(1)
        style = dict(bd=2, relief='raised', font='courier 10 bold', bg='#FFFFFF', anchor='w')
        self.label = tk.Label(self, **{**style, **kwargs})
        self.label.grid(row=0, column=0, sticky='w')
        self.fout:bool = False
        
    def bind(self, target:Widget, text:str, **kwargs):
        target.bind('<Enter>', lambda e: self.fadein(0, text, e))
        target.bind('<Leave>', lambda e: self.fadeout(1-ToolTip.FADE_INC, e))
        
    def fadein(self, alpha:float, text:str=None, event:tk.Event=None):
        if event and text:
            if self.fout:
                self.attributes('-alpha', 0)
                self.fout = False
            self.label.configure(text=f'{text:^{len(text)+2}}')
            self.update()
            offset_x = event.widget.winfo_width()+2
            offset_y = int((event.widget.winfo_height()-self.label.winfo_height())/2)
            w = self.label.winfo_width()
            h = self.label.winfo_height()
            x = event.widget.winfo_rootx()+offset_x
            y = event.widget.winfo_rooty()+offset_y
            self.geometry(f'{w}x{h}+{x}+{y}')
               
        if not self.fout:
            self.attributes('-alpha', alpha)
        
            if alpha < 1:
                self.after(ToolTip.FADE_MS, lambda: self.fadein(min(alpha+ToolTip.FADE_INC, 1)))

    def fadeout(self, alpha:float, event:tk.Event=None):
        if event:
            self.fout = True
               
        if self.fout:
            self.attributes('-alpha', alpha)
            if alpha > 0:
                self.after(ToolTip.FADE_MS, lambda: self.fadeout(max(alpha-ToolTip.FADE_INC, 0)))

if __name__ == '__main__':
    root_window = RootWindow()
    root_window.title('BLTS Installer and Migration Tool')
    root_window.mainloop()