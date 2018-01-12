import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler

import network as net

class Model:
	def __init__(self, is_cuda=False):
		# Save path (models, results)
		self.save_path = "180112-1229" #"YYMMDD_HHMM"

		# Training settings
		self.is_cuda = is_cuda
		self.batch_size = 16
		self.total_epoch = 10
		self.buffer_size = 0

		# Network architecture
		self.residual_num = 4 # the number of residual blocks (6 was used in the paper)
		self.d_first_kernels = 16
		self.d_norm = "batch"
		self.g_norm = "batch"
		self.d_dropout_mask = [0, 0, 0, 0, 0]

		# Hyperparameters
		self.g_lr = 0.0002 # (0.0002 on the paper)
		self.d_lr = 0.0001 # (0.0001 on the paper)
		self.step_size = 10 # (100 on the paper)
		self.gamma = 0.1
		self.cc_lambda = 10 # lambda of cycle-consistency loss (10 on the paper)
		self.tvd_lambda = 5

		# Discriminators and generators
		self.g_a = net.G_128(residual_num=self.residual_num, norm=self.g_norm)
		self.d_a = net.D_128(first_kernels=self.d_first_kernels, norm=self.d_norm, dropout_mask=self.d_dropout_mask)
		self.g_b = net.G_128(residual_num=self.residual_num, norm=self.g_norm)
		self.d_b = net.D_128(first_kernels=self.d_first_kernels, norm=self.d_norm, dropout_mask=self.d_dropout_mask)

		# Loss Function
		self.criterion_GAN = nn.MSELoss()
		self.criterion_CC = nn.L1Loss()

		# Optimizer
		self.g_a_optim = optim.Adam(self.g_a.parameters(), lr=self.g_lr)
		self.d_a_optim = optim.Adam(self.d_a.parameters(), lr=self.d_lr)
		self.g_b_optim = optim.Adam(self.g_b.parameters(), lr=self.g_lr)
		self.d_b_optim = optim.Adam(self.d_b.parameters(), lr=self.d_lr)

		# Scheduler
		self.g_a_scheduler = lr_scheduler.StepLR(self.g_a_optim, step_size=self.step_size, gamma=self.gamma)
		self.d_a_scheduler = lr_scheduler.StepLR(self.d_a_optim, step_size=self.step_size, gamma=self.gamma)
		self.g_b_scheduler = lr_scheduler.StepLR(self.g_b_optim, step_size=self.step_size, gamma=self.gamma)
		self.d_b_scheduler = lr_scheduler.StepLR(self.d_b_optim, step_size=self.step_size, gamma=self.gamma)

		# If cuda is available, activate it
		if(self.is_cuda):
			self.g_a = self.g_a.cuda()
			self.d_a = self.d_a.cuda()
			self.g_b = self.g_b.cuda()
			self.d_b = self.d_b.cuda()

		self.print_info()

	def zero_grad_all(self):
		self.g_a.zero_grad()
		self.d_a.zero_grad()
		self.g_b.zero_grad()
		self.d_b.zero_grad()	

	def scheduler_step(self):
		self.g_a_scheduler.step()
		self.d_a_scheduler.step()
		self.g_b_scheduler.step()
		self.d_b_scheduler.step()

	def print_info(self):
		print("\n[Information] =================================================\n")
		print("Batch Size: %d, Total Epochs: %d, Residual Blocks: %d, CUDA: %r"%(self.batch_size, self.total_epoch, self.residual_num, self.is_cuda))
		print("LR Gen: %1.1E, LR Dis: %1.1E (Step Size: %d, Gamma: %.2f)"%(self.g_lr, self.d_lr, self.step_size, self.gamma))
		print("CC Lambda: %.2f"%(self.cc_lambda))
		print("\n===============================================================\n")