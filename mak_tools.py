
mak_tools_edition = 20211027

import warnings
warnings.filterwarnings("ignore")

import os
import time
import shutil

from tensorboardX import SummaryWriter
import platform
import numpy as np
import datetime

# logger settings
time_format = "%Y%m%d_%H%M"
dir_logger_file_backup = 'file_backup'
dir_model_save = 'model_save'
dir_tensorboard = 'tensorboard'
dir_tensorboard_backup_suffix = '_backup'
dir_log_state = 'log_state.npy'
dir_print_log = 'print_log.txt'
dir_log_name = 'log'

'''
dir_base/
    dir_logger_base/
        dir_log/
            dir_file_backup/
        dir_file_model_save/
        dir_print_log/
        dir_tb/
        print_log.txt
        log_state.npy
'''


class mak_logger:
    def __init__(self, batch_size, train_set_len, train_set_ratio, save_interval=1, backup_time_interval=1 * 60 * 60, name='', dir_base=''):

        self.batch_size = batch_size
        self.train_set_len = train_set_len
        self.save_interval = save_interval
        self.backup_time_interval = backup_time_interval
        self.train_set_ratio = train_set_ratio

        self.epoch = 0
        self.step = 0
        self.dir_backup_model = ''
        self.dir_last_model_int = ''
        self.epoch_last_int = 0

        self.time_start = datetime.datetime.now()

        if not os.path.isdir(dir_base):
            os.mkdir(dir_base)
        self.dir_logger_base = os.path.join(dir_base, name)
        if not os.path.isdir(self.dir_logger_base):
            os.mkdir(self.dir_logger_base)

        self.dir_log = os.path.join(self.dir_logger_base,
                                    dir_log_name + '_' + time.strftime(time_format, time.localtime()))
        if os.path.isdir(self.dir_log):
            self.dir_log = self.dir_log + time.strftime("%S", time.localtime())
        os.mkdir(self.dir_log)

        self.dir_file_backup = os.path.join(self.dir_log, dir_logger_file_backup)
        if not os.path.isdir(self.dir_file_backup):
            os.mkdir(self.dir_file_backup)

        self.dir_file_model_save = os.path.join(self.dir_logger_base, dir_model_save)
        if not os.path.isdir(self.dir_file_model_save):
            os.mkdir(self.dir_file_model_save)

        self.dir_print_log = os.path.join(self.dir_logger_base, dir_print_log)
        if not os.path.isfile(self.dir_print_log):
            print_log = open(self.dir_print_log, 'w')
            print_log.close()

        self.__writer_list = []
        self.__writer_name_list = []
        self.dir_tb = os.path.join(self.dir_logger_base, dir_tensorboard)
        if not os.path.isdir(self.dir_tb):
            os.mkdir(self.dir_tb)
        self.dir_tb_backup = self.dir_tb + dir_tensorboard_backup_suffix
        if not os.path.isdir(self.dir_tb_backup):
            os.mkdir(self.dir_tb_backup)
        self.print('tensorboardX writer has been set. use command to enable it:')
        self.print(f'tensorboard --logdir {os.path.join(os.getcwd(), self.dir_tb)}')

        self.dir_log_state = os.path.join(self.dir_logger_base, dir_log_state)

        if os.path.isfile(self.dir_log_state):
            self.load_log_state(self.dir_log_state)

        self.__save_log_state()

    def file_backup(self, file_list):
        for file in file_list:
            if os.path.isfile(file):
                shutil.copy(file, self.dir_file_backup)
            else:
                print(f'back up file {file} does not exists')

    def __get_writer(self, name):
        if name in self.__writer_name_list:
            index = self.__writer_name_list.index(name)
            return self.__writer_list[index], index
        else:
            if len(self.__writer_name_list) > 10:
                print('requesting too many writers')
                return None, None
            else:
                self.__writer_name_list.append(name)

                new_writer = SummaryWriter(os.path.join(self.dir_tb, name))
                self.__writer_list.append(new_writer)
                return new_writer, self.__writer_name_list.index(name)

    def add_scalar(self, type, data_name, data, time):
        writer, index = self.__get_writer(type)

        writer.add_scalar(tag=data_name, scalar_value=data, global_step=time)

    def step_update(self, add=1):
        self.step += add
        self.epoch += add * self.batch_size * self.train_set_ratio / self.train_set_len

    def watch(self, type, data_name, data, interval=100):  # required to be run at all steps
        if (self.step - 1) % interval == 0:
            self.add_scalar(type, data_name, data, self.step)
            return True
        else:
            return False

    def checkpoint(self, suffix='.pth'):
        now = datetime.datetime.now()
        if (now - self.time_start).seconds > self.backup_time_interval:
            self.time_start = now

            if os.path.isdir(self.dir_tb_backup):
                shutil.rmtree(self.dir_tb_backup)
            shutil.copytree(self.dir_tb, self.dir_tb_backup)

            if self.epoch - self.epoch_last_int >= self.save_interval:
                self.epoch_last_int = int(self.epoch)
                if os.path.isfile(self.dir_backup_model) and self.dir_backup_model != self.dir_last_model_int:
                    os.remove(self.dir_backup_model)
                self.dir_last_model_int = os.path.join(self.dir_file_model_save,
                                                       'epoch_' + str(self.epoch_last_int) + suffix)

                self.dir_backup_model = self.dir_last_model_int

                self.__save_log_state()
                return self.dir_last_model_int
            else:
                if os.path.isfile(self.dir_backup_model) and self.dir_backup_model != self.dir_last_model_int:
                    os.remove(self.dir_backup_model)
                self.dir_backup_model = os.path.join(self.dir_file_model_save,
                                                     'backup_epoch_' + str(round(self.epoch, 2)) + suffix)

                self.__save_log_state()
                return self.dir_backup_model
        else:
            return ''

    def __save_log_state(self):
        dic = {'epoch': self.epoch,
               'epoch_last_int': self.epoch_last_int,
               'dir_last_model_int': self.dir_last_model_int,
               'dir_backup_model': self.dir_backup_model,
               'step': self.step,
               'mak_tools_edition': mak_tools_edition}
        np.save(self.dir_log_state, dic)

    def load_log_state(self, dir_state_file):
        state = np.load(dir_state_file, allow_pickle=True).item()

        if state['mak_tools_edition'] is None:
            self.epoch = state['epoch']
            self.epoch_last_int = state['epoch']
            self.dir_last_model_int = state['dir_last_model']
            self.dir_backup_model = state['dir_last_model']
            self.step = state['step']
        elif state['mak_tools_edition'] >= 20211017:
            self.epoch = state['epoch']
            self.epoch_last_int = state['epoch_last_int']
            self.dir_last_model_int = state['dir_last_model_int']
            self.dir_backup_model = state['dir_backup_model']
            self.step = state['step']

            if os.path.isdir(self.dir_tb_backup):
                if os.path.isdir(self.dir_tb):
                    shutil.rmtree(self.dir_tb)
                shutil.copytree(self.dir_tb_backup, self.dir_tb)

        self.print('log state loaded successfully')
        self.print(f'continue training from epoch = {round(self.epoch, 2)}, dir_last_model = {self.dir_backup_model}')

    def epoch_control(self, max_epoch):
        return range(int(self.epoch / self.train_set_ratio), int(max_epoch / self.train_set_ratio))

    def print(self, message, mode='both'):
        print_log = open(self.dir_print_log, 'a')
        if mode == 'both':
            print(message)
            print_log.write(f'<{time.strftime("%Y%m%d_%H:%M:%S", time.localtime())}> ' + message + '\n')
        elif mode == 'file':
            print_log.write(f'<{time.strftime("%Y%m%d_%H:%M:%S", time.localtime())}> ' + message + '\n')
        elif mode == 'terminal':
            print(message)
        print_log.close()


class mak_f1:
    def __init__(self, tag_len):
        self.len = tag_len
        self.r1_p1_total = np.zeros(self.len)
        self.r1_pa_total = np.zeros(self.len)
        self.ra_p1_total = np.zeros(self.len)

    def batch_update(self, real, pred, need_result='False'):
        r1_p1 = []
        r1_pa = []
        ra_p1 = []
        for i in range(0, self.len):
            r1_pa_ele = sum(real[:, i])
            ra_p1_ele = sum(pred[:, i])
            r1_p1_ele = sum(pred[:, i] * real[:, i])
            r1_p1.append(r1_p1_ele)
            r1_pa.append(r1_pa_ele)
            ra_p1.append(ra_p1_ele)

        self.r1_p1_total += np.array(r1_p1)
        self.r1_pa_total += np.array(r1_pa)
        self.ra_p1_total += np.array(ra_p1)

        if need_result:
            batch_p = self.cal_p(np.array(r1_p1), np.array(ra_p1))
            batch_r = self.cal_r(np.array(r1_p1), np.array(r1_pa))
            batch_f1 = self.cal_f1(batch_p, batch_r)
            return batch_p, batch_r, batch_f1

    def total_result(self):
        p = self.cal_p(self.r1_p1_total, self.ra_p1_total)
        r = self.cal_r(self.r1_p1_total, self.r1_pa_total)
        f1 = self.cal_f1(p, r)
        p_avg = np.mean(p)
        r_avg = np.mean(r)
        f1_avg = np.mean(f1)

        return p, p_avg, r, r_avg, f1, f1_avg

    def total_result_str(self):
        p, p_avg, r, r_avg, f1, f1_avg = self.total_result()
        result_str = f"p : {str(['%.3f' % i for i in p])}, avg: {p_avg}\n"
        result_str += f"r : {str(['%.3f' % i for i in r])}, avg: {r_avg}\n"
        result_str += f"f1 : {str(['%.3f' % i for i in f1])}, avg:{f1_avg}"
        return result_str

    def cal_p(self, r1_p1, ra_p1):
        if type(r1_p1) == list:
            return np.array(r1_p1) / np.array(ra_p1)
        else:
            return r1_p1 / ra_p1

    def cal_r(self, r1_p1, r1_pa):
        if type(r1_p1) == list:
            return np.array(r1_p1) / np.array(r1_pa)
        else:
            return r1_p1 / r1_pa

    def cal_f1(self, p, r):
        if type(p) == list:
            return 2 * np.array(p) * np.array(r) / (np.array(p) + np.array(r))
        else:
            return 2 * p * r / (p + r)




