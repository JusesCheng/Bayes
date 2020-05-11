# -*- coding: utf-8 -*-
"""
Created on Mon May 11 19:39:17 2020

@author: OU
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QMessageBox, QAction
from PyQt5.QtCore import QCoreApplication , Qt
from PyQt5.QtGui import QPixmap, QIcon, QMovie
from PyQt5 import QtGui
from homework import Ui_MainWindow
import scipy.stats as stats
import numpy as np
import matplotlib.mlab as mlab
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.mlab as mlab
import scipy.stats as stats
from PyQt5.Qt import QThreadPool
#from call_k_means import Run_k_means
from sklearn import metrics
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
# look homework by E
#------------------------------------------------------------------
class MyFigure(FigureCanvas): #畫布的大小
    def __init__(self,parent=None,width=5, height=4, dpi=100):
        plt.style.use("ggplot")
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(True)
        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        

#------------
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.mpl = MyFigure(self,width=10, height=10, dpi=100) 
#        self.fig_roc = MyFigure(self,width = 4, height = 5, dpi = 100)
        
        self.ui.pushButton.clicked.connect(self.pushButton_Click)#畫圖
        self.ui.pushButton_3.clicked.connect(self.pushButton_3_Click) #貝氏
#        self.ui.pushButton_4.clicked.connect(self.pushButton_4_Click)  #K-means(先挖
        
        self.mpl_ntb = NavigationToolbar(self.mpl,self)
        
        self.ui.verticalLayout.addWidget(self.mpl)
        self.ui.verticalLayout.addWidget(self.mpl_ntb)
        self.show()
        
    def throw_coin(self, rounds, times, threshold):
        toss_coin = np.random.rand(rounds, times)
        toss_coin[toss_coin >= threshold] = 1
        toss_coin[toss_coin < threshold] = 0   #小於閥值就是反面
        
        toss_coin = 1 - toss_coin        
        toss_coin = np.sum(toss_coin, 1)
        return toss_coin
    
    def calc_fitting_curve(self, toss_coin, toss_coin_count, times):  #計算擬合曲線
        mu = toss_coin.mean()
        sigma = toss_coin.std()
        y = stats.norm.pdf(range(times + 1), mu, sigma)
        max_n = np.max(toss_coin_count)
        max_y = np.max(y)
        factor = max_n/max_y
        return y, factor
    
    def close_mpl(self): #close其他圖才能重新畫
        self.mpl.axes.clear()

        
    def pushButton_Click(self):
        if self.ui.lineEdit.text() == '0' \
        or self.ui.lineEdit_2.text() == '0' \
        or self.ui.lineEdit_3.text() == '0' \
        or self.ui.lineEdit_4.text() == '0' \
        or self.ui.lineEdit_5.text() == '0' \
        or self.ui.lineEdit_6.text() == '0' :
            QMessageBox.about(self, 'Error', 'input parameter plz')
        else:
            self.close_mpl()
            
        
        rounds1 = int(self.ui.lineEdit.text())#n1
        times1 = int(self.ui.lineEdit_2.text())#d1
        threshold1 = float(self.ui.lineEdit_3.text())
        
        rounds2 = int(self.ui.lineEdit_4.text())#n2
        times2 = int(self.ui.lineEdit_5.text())#d2
        threshold2 = float(self.ui.lineEdit_6.text())
        
        #丟硬幣 -------
        toss_coin1 = self.throw_coin(rounds1, times1, threshold1)
        toss_coin2 = self.throw_coin(rounds2, times2, threshold2)
        
        #統計不同次數回合數 補0到times的長度
        toss_coin1_count = self.appendzeros(np.bincount(toss_coin1.tolist()), times1)
        toss_coin2_count = self.appendzeros(np.bincount(toss_coin2.tolist()), times2)
        
        #畫直方圖
        self.mpl.axes.bar(range(times1 + 1), toss_coin1_count,  edgecolor = 'black', alpha=.5)
        self.mpl.axes.bar(range(times2 + 1), toss_coin2_count,  edgecolor = 'black', alpha=.5)
        
        #畫擬合曲線
        y1, factor1 = self.calc_fitting_curve(toss_coin1, toss_coin1_count, times1)
        y2, factor2 = self.calc_fitting_curve(toss_coin2, toss_coin2_count, times2)
        
        self.mpl.axes.plot(range(times1 + 1), y1*factor1, 'm--', color = 'green', linewidth = 2)
        self.mpl.axes.plot(range(times2 + 1), y2*factor2, 'm--', color = 'red', linewidth = 2)
        
        self.mpl.draw()
        
        #存資料
        self.coin_dict = dict()
        self.coin_dict['times1'] = times1
        self.coin_dict['times2'] = times2
        self.coin_dict['toss_coin1'] = toss_coin1
        self.coin_dict['toss_coin2'] = toss_coin2
        self.coin_dict['y1'] = y1
        self.coin_dict['y2'] = y2
        self.coin_dict['factor1'] = factor1
        self.coin_dict['factor2'] = factor2
        self.coin_dict['toss_coin1_count'] = toss_coin1_count
        self.coin_dict['toss_coin2_count'] = toss_coin2_count
        
        #存0陣列避免拿不出資料
        self.coin_dict['toss_coin3'] = np.zeros(101)
        self.coin_dict['toss_coin3_count'] = np.zeros(101)
        
    def appendzeros(self, bincount, times):  #補0到補到 times+1 的長度
        appendlen = times - len(bincount) + 1  #看要補幾格0
        if appendlen > 0:
            appendarr = np.zeros(appendlen)
            bincount = np.hstack((bincount, appendarr))           
        return bincount
    def replot_now(self):  #因為刷新都會把畫布清空，所以我重畫原本的直方圖
        times1 = self.coin_dict['times1']
        times2 = self.coin_dict['times2']
        y1 = self.coin_dict['y1']
        y2 = self.coin_dict['y2']
        factor1 = self.coin_dict['factor1']
        factor2 = self.coin_dict['factor2'] 
        toss_coin1_count = self.coin_dict['toss_coin1_count']
        toss_coin2_count = self.coin_dict['toss_coin2_count']
        
        #畫直方圖
        self.mpl.axes.bar(range(times1 + 1), toss_coin1_count, edgecolor = 'black', alpha=.5)
        self.mpl.axes.bar(range(times2 + 1), toss_coin2_count, edgecolor = 'black', alpha=.5)
    
        #畫擬合曲線
        self.mpl.axes.plot(range(times1 + 1), y1*factor1, 'm--', color = 'green', linewidth = 2)       
        self.mpl.axes.plot(range(times2 + 1), y2*factor2, 'm--', color = 'red', linewidth = 2)
        
        self.mpl.draw()
    def find_Bayes_line(self, toss_coin1_count, toss_coin2_count, times):  #找貝氏分類線
        #toss_coin1_count是第一顆硬幣丟0~100次正面分別有幾個回合的array
        last_coin = 'None'  #前一次最高硬幣
        current_coin = 'None'  #當前最高硬幣
        
        for i in range(times + 1):
            last_coin = current_coin  #跑新一輪就儲存上一輪的最高硬幣
            if toss_coin1_count[i] == 0 and toss_coin2_count[i] == 0:  #都是0就不要做
                continue
            elif toss_coin1_count[i] >= toss_coin2_count[i]:  #如果 Coin1 在 times = i 時比 Coin2 高
                current_coin = 'Coin1'
            elif toss_coin1_count[i] < toss_coin2_count[i]:  #如果 Coin2 在 times = i 時比 Coin1 高
                current_coin = 'Coin2'
            
            if last_coin != current_coin and last_coin != 'None':
                ans = i  #貝氏分類的解答
                break
        return ans  
    def calc_classification_rate(self, toss_coin1, toss_coin2, divide_value):
        #Coin1固定在左邊，Coin2固定在左邊
        #toss_coin1_count是第一顆硬幣丟0~100次正面分別有幾個回合的array
        #divide_value是分割線的值
        
        if toss_coin1.min() <= toss_coin2.min():
            toss_coin1_copy = toss_coin1.copy()
            toss_coin2_copy = toss_coin2.copy()
        else:
            toss_coin1_copy = toss_coin2.copy()
            toss_coin2_copy = toss_coin1.copy()
            
        #計算線左邊是Coin1的有幾個(tp)，線右邊是Coin2的有幾個(tn)
        toss_coin1_copy[toss_coin1_copy <= divide_value] = 1
        toss_coin1_copy[toss_coin1_copy > divide_value] = 0
        toss_coin2_copy[toss_coin2_copy < divide_value] = 0
        toss_coin2_copy[toss_coin2_copy >= divide_value] = 1  
        
        tp = np.sum(toss_coin1_copy)
        fn = len(toss_coin1_copy) - tp
        tn = np.sum(toss_coin2_copy)
        fp = len(toss_coin2_copy) - tn
        
        tpr = tp/(tp + fn)
        fpr = fp/(fp + tn)
        
        acc = (tp + tn) / (tp + fn + tn + fp)
        auc = metrics.auc([0, fpr, 1], [0, tpr, 1])
        
        return tp, fn, tn, fp, tpr, fpr, acc, auc 
    
    
    


#    def pushButton_3_Click(self): #畫bias
#        if self.ui.lineEdit.text() == '0' \
#        or self.ui.lineEdit_2.text() == '0' \
#        or self.ui.lineEdit_3.text() == '0' \
#        or self.ui.lineEdit_4.text() == '0' \
#        or self.ui.lineEdit_5.text() == '0'\
#        or self.ui.lineEdit_6.text() == '0' :
#            QMessageBox.about(self, 'Error', 'input parameter plz')
#        else:
#            self.close_mpl()
    def pushButton_3_Click(self):  #貝氏分類器
        toss_coin1 = self.coin_dict['toss_coin1']
        toss_coin2 = self.coin_dict['toss_coin2']
                
        times1 = self.coin_dict['times1']
#        times2 = self.coin_dict['times2']#由d決定要存甚麼
        
        toss_coin1_count = self.coin_dict['toss_coin1_count']
        toss_coin2_count = self.coin_dict['toss_coin2_count']        
        
#        if self.ui.checkBox.isChecked() == False:  #如果沒有勾使用第3個硬幣
        #貝氏分類
        ans = self.find_Bayes_line(toss_coin1_count, toss_coin2_count, times1)
        
        #畫分類線
        textheight = max(toss_coin1_count.max(), toss_coin2_count.max())  #文字的高度選柱子最高點
        
        self.close_mpl()
        self.replot_now()
        
        self.mpl.axes.axvline(x = ans, linewidth = 2, color = 'brown')
        self.mpl.axes.text(ans+2, textheight, str(ans))
        
        self.mpl.draw()
             
        #算分類率
        tp, fn, tn, fp, tpr, fpr, acc, auc = self.calc_classification_rate(toss_coin1, toss_coin2, ans)       
#            print('\ntp:%d\nfn:%d\ntn:%d\nfp:%d\ntpr:%f\nfpr:%f\nacc:%f\nauc:%f\n' %(tp, fn, tn, fp, tpr, fpr, acc, auc))
      
        #左P 右N
        self.ui.label_11.setText('TP: %d' %(tp))
        self.ui.label_12.setText('FN: %d' %(fn))
        self.ui.label_13.setText('TN: %d' %(tn))
        self.ui.label_14.setText('FP: %d' %(fp))
        self.ui.label_15.setText('TPR: %.3f' %(tpr))
        self.ui.label_16.setText('FPR: %.3f' %(fpr))
        self.ui.label_17.setText('ACC: %.3f' %(acc))
        self.ui.label_18.setText('AUC: %.3f' %(auc))
        
        #左N 右P
        tpr = tn/(tn + fp)
        fpr = fp/(fn + tp)
        auc = metrics.auc([0, fpr, 1], [0, tpr, 1])
        
                   
        self.ui.label_20.setText('TP: %d' %(tn))
        self.ui.label_21.setText('FN: %d' %(fp))
        self.ui.label_22.setText('TN: %d' %(tp))
        self.ui.label_23.setText('FP: %d' %(fn))
        self.ui.label_24.setText('TPR: %.3f' %(tpr))
        self.ui.label_25.setText('FPR: %.3f' %(fpr))
        self.ui.label_26.setText('ACC: %.3f' %(acc))
        self.ui.label_27.setText('AUC: %.3f' %(auc))
            

    
            
        

    
app = QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())