<template>
  <div class="account-management">
    <div class="page-header">
      <h1>账号管理</h1>
    </div>
    
    <div class="account-tabs">
      <el-tabs v-model="activeTab" class="account-tabs-nav">
        <el-tab-pane label="全部" name="all">
          <div class="account-list-container">
            <div class="account-search">
              <el-input
                v-model="searchKeyword"
                placeholder="输入名称或账号搜索"
                prefix-icon="Search"
                clearable
                @clear="handleSearch"
                @input="handleSearch"
              />
              <div class="action-buttons">
                <el-button type="primary" @click="handleAddAccount">添加账号</el-button>
                <el-button type="info" @click="fetchAccounts" :loading="false">
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span v-if="appStore.isAccountRefreshing">刷新中</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredAccounts.length > 0" class="account-list">
              <el-table :data="filteredAccounts" style="width: 100%">
                <el-table-column label="头像" width="80">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="名称" width="180" />
                <el-table-column prop="platform" label="平台">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="plain"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="plain"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button size="small" type="primary" :icon="Download" @click="handleDownloadCookie(scope.row)">下载Cookie</el-button>
                    <el-button size="small" type="info" :icon="Upload" @click="handleUploadCookie(scope.row)">上传Cookie</el-button>
                    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty description="暂无账号数据" />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="快手" name="kuaishou">
          <div class="account-list-container">
            <div class="account-search">
              <el-input
                v-model="searchKeyword"
                placeholder="输入名称或账号搜索"
                prefix-icon="Search"
                clearable
                @clear="handleSearch"
                @input="handleSearch"
              />
              <div class="action-buttons">
                <el-button type="primary" @click="handleAddAccount">添加账号</el-button>
                <el-button type="info" @click="fetchAccounts" :loading="false">
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span v-if="appStore.isAccountRefreshing">刷新中</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredKuaishouAccounts.length > 0" class="account-list">
              <el-table :data="filteredKuaishouAccounts" style="width: 100%">
                <el-table-column label="头像" width="80">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="名称" width="180" />
                <el-table-column prop="platform" label="平台">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="plain"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="plain"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button size="small" type="primary" :icon="Download" @click="handleDownloadCookie(scope.row)">下载Cookie</el-button>
                    <el-button size="small" type="info" :icon="Upload" @click="handleUploadCookie(scope.row)">上传Cookie</el-button>
                    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty description="暂无快手账号数据" />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="抖音" name="douyin">
          <div class="account-list-container">
            <div class="account-search">
              <el-input
                v-model="searchKeyword"
                placeholder="输入名称或账号搜索"
                prefix-icon="Search"
                clearable
                @clear="handleSearch"
                @input="handleSearch"
              />
              <div class="action-buttons">
                <el-button type="primary" @click="handleAddAccount">添加账号</el-button>
                <el-button type="info" @click="fetchAccounts" :loading="false">
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span v-if="appStore.isAccountRefreshing">刷新中</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredDouyinAccounts.length > 0" class="account-list">
              <el-table :data="filteredDouyinAccounts" style="width: 100%">
                <el-table-column label="头像" width="80">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="名称" width="180" />
                <el-table-column prop="platform" label="平台">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="plain"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="plain"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button size="small" type="primary" :icon="Download" @click="handleDownloadCookie(scope.row)">下载Cookie</el-button>
                    <el-button size="small" type="info" :icon="Upload" @click="handleUploadCookie(scope.row)">上传Cookie</el-button>
                    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty description="暂无抖音账号数据" />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="视频号" name="channels">
          <div class="account-list-container">
            <div class="account-search">
              <el-input
                v-model="searchKeyword"
                placeholder="输入名称或账号搜索"
                prefix-icon="Search"
                clearable
                @clear="handleSearch"
                @input="handleSearch"
              />
              <div class="action-buttons">
                <el-button type="primary" @click="handleAddAccount">添加账号</el-button>
                <el-button type="info" @click="fetchAccounts" :loading="false">
                  <el-icon :class="{ 'is-loading': appStore.isAccountRefreshing }"><Refresh /></el-icon>
                  <span v-if="appStore.isAccountRefreshing">刷新中</span>
                </el-button>
              </div>
            </div>
            
            <div v-if="filteredChannelsAccounts.length > 0" class="account-list">
              <el-table :data="filteredChannelsAccounts" style="width: 100%">
                <el-table-column label="头像" width="80">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="名称" width="180" />
                <el-table-column prop="platform" label="平台">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="plain"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="plain"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button size="small" type="primary" :icon="Download" @click="handleDownloadCookie(scope.row)">下载Cookie</el-button>
                    <el-button size="small" type="info" :icon="Upload" @click="handleUploadCookie(scope.row)">上传Cookie</el-button>
                    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-else class="empty-data">
              <el-empty description="暂无视频号账号数据" />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="小红书(MCP)" name="xiaohongshu">
          <div class="account-list-container">
            <!-- MCP 说明提示 -->
            <el-alert
              title="小红书账号由 xiaohongshu-mcp 服务管理，需先启动 MCP 服务再扫码登录"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />

            <div class="action-buttons" style="margin-bottom: 16px; display:flex; gap:8px">
              <el-button type="primary" @click="handleXhsMcpLogin()">
                <el-icon><Plus /></el-icon>
                MCP 扫码登录
              </el-button>
              <el-button type="info" @click="refreshXhsMcpStatus" :loading="xhsMcpLoading">
                <el-icon :class="{ 'is-loading': xhsMcpLoading }"><Refresh /></el-icon>
                刷新状态
              </el-button>
            </div>

            <!-- MCP 账号状态表 -->
            <el-table :data="xhsMcpAccounts" style="width: 100%" v-loading="xhsMcpLoading">
              <el-table-column prop="name" label="账号名称" width="180" />
              <el-table-column prop="url" label="MCP 地址" width="220" />
              <el-table-column label="服务状态" width="120">
                <template #default="scope">
                  <el-tag :type="scope.row.online ? 'success' : 'danger'" effect="plain">
                    {{ scope.row.online ? '运行中' : '未启动' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="登录状态" width="120">
                <template #default="scope">
                  <el-tag :type="scope.row.logged_in ? 'success' : 'warning'" effect="plain">
                    {{ scope.row.logged_in ? '已登录' : '未登录' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button size="small" type="success" :disabled="scope.row.online"
                    @click="handleXhsMcpStart(scope.row)">启动服务</el-button>
                  <el-button size="small" type="warning" :disabled="!scope.row.online"
                    @click="handleXhsMcpStop(scope.row)">停止服务</el-button>
                  <el-button size="small" type="primary" :disabled="!scope.row.online"
                    @click="handleXhsMcpLogin(scope.row.name)">扫码登录</el-button>
                  <el-button size="small" type="danger"
                    :disabled="!scope.row.online || !scope.row.logged_in"
                    @click="handleXhsMcpLogout(scope.row)">退出登录</el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 未启动提示 -->
            <el-alert v-if="xhsMcpAccounts.some(a => !a.online)" style="margin-top:16px"
              type="warning" :closable="false" show-icon>
              <template #title>有 MCP 实例未启动，请执行以下命令：</template>
              <div v-for="acc in xhsMcpAccounts.filter(a => !a.online)" :key="acc.name" style="margin-top:6px">
                <el-tag type="warning">{{ acc.name }}</el-tag>
                <code style="margin-left:8px;background:#f5f7fa;padding:2px 6px;border-radius:3px">
                  cd D:\xiaohongshu-mcp &amp;&amp; go run . --port {{ acc.url.split(':').pop() }}
                </code>
              </div>
            </el-alert>

            <!-- MCP 账号配置编辑 -->
            <el-card style="margin-top:20px">
              <template #header>
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <span>MCP 账号配置</span>
                  <div>
                    <el-button size="small" type="primary" @click="addMcpConfigRow">添加账号</el-button>
                    <el-button size="small" type="success" @click="saveMcpConfig" :loading="mcpConfigSaving">保存配置</el-button>
                  </div>
                </div>
              </template>
              <el-table :data="mcpConfigList" style="width:100%">
                <el-table-column label="账号名称" min-width="160">
                  <template #default="scope">
                    <el-input v-model="scope.row.name" placeholder="账号名称" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="MCP 地址" min-width="220">
                  <template #default="scope">
                    <el-input v-model="scope.row.url" placeholder="http://localhost:8080" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="scope">
                    <el-button size="small" type="danger" @click="removeMcpConfigRow(scope.$index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div style="margin-top:12px">
                <el-form-item label="默认 MCP 地址" style="margin:0">
                  <el-input v-model="mcpDefaultUrl" placeholder="http://localhost:8080" style="width:260px" size="small" />
                </el-form-item>
              </div>
            </el-card>

            <!-- 占位（保留原列表结构以兼容 filteredXiaohongshuAccounts 计算属性） -->
            <div v-if="false" class="account-list">
              <el-table :data="filteredXiaohongshuAccounts" style="width: 100%">
                <el-table-column label="头像" width="80">
                  <template #default="scope">
                    <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="40" />
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="名称" width="180" />
                <el-table-column prop="platform" label="平台">
                  <template #default="scope">
                    <el-tag
                      :type="getPlatformTagType(scope.row.platform)"
                      effect="plain"
                    >
                      {{ scope.row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template #default="scope">
                    <el-tag
                      :type="getStatusTagType(scope.row.status)"
                      effect="plain"
                      :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                      @click="handleStatusClick(scope.row)"
                    >
                      <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                        <Loading />
                      </el-icon>
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button size="small" type="primary" :icon="Download" @click="handleDownloadCookie(scope.row)">下载Cookie</el-button>
                    <el-button size="small" type="info" :icon="Upload" @click="handleUploadCookie(scope.row)">上传Cookie</el-button>
                    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 小红书 MCP 登录弹窗 -->
    <el-dialog v-model="xhsMcpDialogVisible" title="小红书 MCP 扫码登录" width="420px"
      :close-on-click-modal="false" :show-close="xhsMcpLoginStatus !== 'loading'">
      <div style="margin-bottom:16px" v-if="!xhsMcpLoginStatus || xhsMcpLoginStatus === 'loading'">
        <el-form label-width="80px">
          <el-form-item label="选择账号">
            <el-select v-model="xhsMcpLoginAccount" placeholder="请选择账号" style="width:100%"
              :disabled="xhsMcpLoginStatus === 'loading'">
              <el-option v-for="acc in xhsMcpAccounts" :key="acc.name" :label="acc.name" :value="acc.name">
                <span>{{ acc.name }}</span>
                <el-tag size="small" :type="acc.online ? 'success' : 'danger'" style="margin-left:8px">
                  {{ acc.online ? '在线' : '离线' }}
                </el-tag>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <div style="text-align:center;min-height:260px;display:flex;align-items:center;justify-content:center;flex-direction:column">
        <div v-if="xhsMcpLoginStatus === 'loading'" style="color:#909399">
          <el-icon class="is-loading" style="font-size:32px"><Refresh /></el-icon>
          <p style="margin-top:12px">正在获取二维码，请稍候...</p>
          <p style="font-size:12px;color:#c0c4cc">账号：{{ xhsMcpLoginAccount }}</p>
        </div>
        <div v-else-if="xhsMcpQrCode && !xhsMcpLoginStatus">
          <p style="color:#606266;margin-bottom:12px">请用小红书 App 扫描二维码登录</p>
          <p style="font-size:12px;color:#909399;margin-bottom:12px">账号：{{ xhsMcpLoginAccount }}</p>
          <img :src="xhsMcpQrCode" style="width:200px;height:200px" alt="二维码" />
        </div>
        <div v-else-if="xhsMcpLoginStatus === '200'" style="color:#67c23a">
          <el-icon style="font-size:48px"><CircleCheckFilled /></el-icon>
          <p style="margin-top:12px">登录成功！</p>
        </div>
        <div v-else-if="xhsMcpLoginStatus === '500'" style="color:#f56c6c">
          <el-icon style="font-size:48px"><CircleCloseFilled /></el-icon>
          <p style="margin-top:12px">登录失败，请检查 MCP 服务是否已启动</p>
          <p style="font-size:12px;color:#909399;margin-top:8px">
            启动命令：cd D:\xiaohongshu-mcp &amp;&amp; go run . --port 8080
          </p>
        </div>
      </div>
      <template #footer>
        <el-button @click="xhsMcpDialogVisible = false" :disabled="xhsMcpLoginStatus === 'loading'">关闭</el-button>
        <el-button type="primary" @click="startXhsMcpLogin" :loading="xhsMcpLoginStatus === 'loading'"
          :disabled="!xhsMcpLoginAccount || xhsMcpLoginStatus === '200'">
          {{ xhsMcpLoginStatus === 'loading' ? '连接中...' : '开始登录' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑账号对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加账号' : '编辑账号'"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="!sseConnecting"
      :show-close="!sseConnecting"
    >
      <el-form :model="accountForm" label-width="80px" :rules="rules" ref="accountFormRef">
        <el-form-item label="平台" prop="platform">
          <el-select 
            v-model="accountForm.platform" 
            placeholder="请选择平台" 
            style="width: 100%"
            :disabled="dialogType === 'edit' || sseConnecting"
          >
            <el-option label="快手" value="快手" />
            <el-option label="抖音" value="抖音" />
            <el-option label="视频号" value="视频号" />
            <el-option label="小红书" value="小红书" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input 
            v-model="accountForm.name" 
            placeholder="请输入账号名称" 
            :disabled="sseConnecting"
          />
        </el-form-item>
        
        <!-- 二维码显示区域 -->
        <div v-if="sseConnecting" class="qrcode-container">
          <div v-if="qrCodeData && !loginStatus" class="qrcode-wrapper">
            <p class="qrcode-tip">请使用对应平台APP扫描二维码登录</p>
            <img :src="qrCodeData" alt="登录二维码" class="qrcode-image" />
          </div>
          <div v-else-if="!qrCodeData && !loginStatus" class="loading-wrapper">
            <el-icon class="is-loading"><Refresh /></el-icon>
            <span>请求中...</span>
          </div>
          <div v-else-if="loginStatus === '200'" class="success-wrapper">
            <el-icon><CircleCheckFilled /></el-icon>
            <span>添加成功</span>
          </div>
          <div v-else-if="loginStatus === '500'" class="error-wrapper">
            <el-icon><CircleCloseFilled /></el-icon>
            <span>添加失败，请稍后再试</span>
          </div>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitAccountForm" 
            :loading="sseConnecting" 
            :disabled="sseConnecting"
          >
            {{ sseConnecting ? '请求中' : '确认' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { Refresh, CircleCheckFilled, CircleCloseFilled, Download, Upload, Loading, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountApi } from '@/api/account'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { http } from '@/utils/request'

// 获取账号状态管理
const accountStore = useAccountStore()
// 获取应用状态管理
const appStore = useAppStore()

// 当前激活的标签页
const activeTab = ref('all')

// 搜索关键词
const searchKeyword = ref('')

// 获取账号数据（快速，不验证）
const fetchAccountsQuick = async () => {
  try {
    const res = await accountApi.getAccounts()
    if (res.code === 200 && res.data) {
      // 将所有账号的状态暂时设为"验证中"
      const accountsWithPendingStatus = res.data.map(account => {
        const updatedAccount = [...account];
        updatedAccount[4] = -1; // -1 表示验证中的临时状态
        return updatedAccount;
      });
      accountStore.setAccounts(accountsWithPendingStatus);
    }
  } catch (error) {
    console.error('快速获取账号数据失败:', error)
  }
}

// 获取账号数据（带验证）
const fetchAccounts = async () => {
  if (appStore.isAccountRefreshing) return

  appStore.setAccountRefreshing(true)

  try {
    const res = await accountApi.getValidAccounts()
    if (res.code === 200 && res.data) {
      accountStore.setAccounts(res.data)
      ElMessage.success('账号数据获取成功')
      // 标记为已访问
      if (appStore.isFirstTimeAccountManagement) {
        appStore.setAccountManagementVisited()
      }
    } else {
      ElMessage.error('获取账号数据失败')
    }
  } catch (error) {
    console.error('获取账号数据失败:', error)
    ElMessage.error('获取账号数据失败')
  } finally {
    appStore.setAccountRefreshing(false)
  }
}

// 后台验证所有账号（优化版本，使用setTimeout避免阻塞UI）
const validateAllAccountsInBackground = async () => {
  // 使用setTimeout将验证过程放在下一个事件循环，避免阻塞UI
  setTimeout(async () => {
    try {
      const res = await accountApi.getValidAccounts()
      if (res.code === 200 && res.data) {
        accountStore.setAccounts(res.data)
      }
    } catch (error) {
      console.error('后台验证账号失败:', error)
    }
  }, 0)
}

// 页面加载时获取账号数据
onMounted(() => {
  // 快速获取账号列表（不验证），立即显示
  fetchAccountsQuick()

  // 在后台验证所有账号
  setTimeout(() => {
    validateAllAccountsInBackground()
  }, 100)

  // 自动拉取小红书 MCP 状态
  refreshXhsMcpStatus()
  // 加载 MCP 配置
  loadMcpConfig()
})

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  const typeMap = {
    '快手': 'success',
    '抖音': 'danger',
    '视频号': 'warning',
    '小红书': 'info'
  }
  return typeMap[platform] || 'info'
}

// 判断状态是否可点击（异常状态可点击）
const isStatusClickable = (status) => {
  return status === '异常'; // 只有异常状态可点击，验证中不可点击
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  if (status === '验证中') {
    return 'info'; // 验证中使用灰色
  } else if (status === '正常') {
    return 'success'; // 正常使用绿色
  } else {
    return 'danger'; // 无效使用红色
  }
}

// 处理状态点击事件
const handleStatusClick = (row) => {
  if (isStatusClickable(row.status)) {
    // 触发重新登录流程
    handleReLogin(row)
  }
}

// 过滤后的账号列表
const filteredAccounts = computed(() => {
  if (!searchKeyword.value) return accountStore.accounts
  return accountStore.accounts.filter(account =>
    account.name.includes(searchKeyword.value)
  )
})

// 按平台过滤的账号列表
const filteredKuaishouAccounts = computed(() => {
  return filteredAccounts.value.filter(account => account.platform === '快手')
})

const filteredDouyinAccounts = computed(() => {
  return filteredAccounts.value.filter(account => account.platform === '抖音')
})

const filteredChannelsAccounts = computed(() => {
  return filteredAccounts.value.filter(account => account.platform === '视频号')
})

const filteredXiaohongshuAccounts = computed(() => {
  return filteredAccounts.value.filter(account => account.platform === '小红书')
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已通过计算属性实现
}

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' 或 'edit'
const accountFormRef = ref(null)

// 账号表单
const accountForm = reactive({
  id: null,
  name: '',
  platform: '',
  status: '正常'
})

// 表单验证规则
const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  name: [{ required: true, message: '请输入账号名称', trigger: 'blur' }]
}

// ==================== 小红书 MCP 管理 ====================
const xhsMcpAccounts = ref([])
const xhsMcpLoading = ref(false)
const xhsMcpDialogVisible = ref(false)
const xhsMcpLoginAccount = ref('')
const xhsMcpQrCode = ref('')
const xhsMcpLoginStatus = ref('') // '' | 'loading' | '200' | '500'
let xhsMcpEventSource = null

// 刷新 MCP 状态
const refreshXhsMcpStatus = async () => {
  xhsMcpLoading.value = true
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 70000) // 70s timeout
    const res = await fetch(`${baseUrl}/xhs/mcp/status`, { signal: controller.signal }).then(r => r.json())
    clearTimeout(timer)
    if (res.code === 200) {
      xhsMcpAccounts.value = Object.entries(res.data).map(([name, info]) => ({ name, ...info }))
    }
  } catch (e) {
    if (e.name === 'AbortError') {
      ElMessage.warning('MCP 状态查询超时（首次启动 Chrome 较慢，请稍后重试）')
    } else {
      ElMessage.error('获取 MCP 状态失败，请检查后端服务')
    }
  } finally {
    xhsMcpLoading.value = false
  }
}

// 弹出 MCP 登录对话框
const handleXhsMcpLogin = (accountName = '') => {
  xhsMcpLoginAccount.value = accountName || (xhsMcpAccounts.value[0]?.name || '')
  xhsMcpQrCode.value = ''
  xhsMcpLoginStatus.value = ''
  xhsMcpDialogVisible.value = true
}

// 开始 MCP 登录（连接 SSE）
const startXhsMcpLogin = () => {
  if (!xhsMcpLoginAccount.value) {
    ElMessage.warning('请选择账号')
    return
  }
  xhsMcpQrCode.value = ''
  xhsMcpLoginStatus.value = 'loading'

  if (xhsMcpEventSource) { xhsMcpEventSource.close(); xhsMcpEventSource = null }

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
  const url = `${baseUrl}/xhs/mcp/login?account=${encodeURIComponent(xhsMcpLoginAccount.value)}`
  xhsMcpEventSource = new EventSource(url)

  xhsMcpEventSource.onmessage = (e) => {
    const data = e.data.trim()
    if (data === '200') {
      xhsMcpLoginStatus.value = '200'
      xhsMcpEventSource.close()
      setTimeout(() => {
        xhsMcpDialogVisible.value = false
        refreshXhsMcpStatus()
        ElMessage.success(`${xhsMcpLoginAccount.value} 登录成功`)
      }, 1500)
    } else if (data === '500') {
      xhsMcpLoginStatus.value = '500'
      xhsMcpEventSource.close()
    } else if (data.length > 100) {
      xhsMcpQrCode.value = data.startsWith('data:') ? data : `data:image/png;base64,${data}`
      xhsMcpLoginStatus.value = ''
    }
  }
  xhsMcpEventSource.onerror = () => {
    xhsMcpLoginStatus.value = '500'
    xhsMcpEventSource.close()
    ElMessage.error('连接 MCP 服务失败，请确认服务已启动')
  }
}

// 启动 MCP 服务
const handleXhsMcpStart = async (account) => {
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
    const res = await fetch(`${baseUrl}/xhs/mcp/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account: account.name })
    }).then(r => r.json())
    ElMessage.success(res.msg || '服务启动中...')
    setTimeout(refreshXhsMcpStatus, 3000)
  } catch (e) {
    ElMessage.error('启动失败，请手动启动 MCP 服务')
  }
}

// 停止 MCP 服务
const handleXhsMcpStop = async (account) => {
  try {
    await ElMessageBox.confirm(`确认停止 ${account.name} 的 MCP 服务？`, '提示', {
      confirmButtonText: '确认停止', cancelButtonText: '取消', type: 'warning'
    })
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
    const res = await fetch(`${baseUrl}/xhs/mcp/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account: account.name })
    }).then(r => r.json())
    ElMessage.success(res.msg || '服务已停止')
    setTimeout(refreshXhsMcpStatus, 1000)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('停止失败')
  }
}

// ==================== MCP 配置管理 ====================
const mcpConfigList = ref([])
const mcpDefaultUrl = ref('http://localhost:8080')
const mcpConfigSaving = ref(false)

const loadMcpConfig = async () => {
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
    const res = await fetch(`${baseUrl}/xhs/mcp/config`).then(r => r.json())
    if (res.code === 200) {
      mcpConfigList.value = res.data.accounts.map(a => ({ ...a }))
      mcpDefaultUrl.value = res.data.defaultUrl
    }
  } catch (e) {
    console.warn('加载 MCP 配置失败:', e)
  }
}

const addMcpConfigRow = () => {
  mcpConfigList.value.push({ name: '', url: 'http://localhost:8080' })
}

const removeMcpConfigRow = (index) => {
  mcpConfigList.value.splice(index, 1)
}

const saveMcpConfig = async () => {
  const invalid = mcpConfigList.value.some(a => !a.name || !a.url)
  if (invalid) {
    ElMessage.warning('账号名称和地址不能为空')
    return
  }
  mcpConfigSaving.value = true
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
    const res = await fetch(`${baseUrl}/xhs/mcp/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accounts: mcpConfigList.value, defaultUrl: mcpDefaultUrl.value })
    }).then(r => r.json())
    if (res.code === 200) {
      ElMessage.success(res.msg || '配置已保存')
      refreshXhsMcpStatus()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败，请检查后端服务')
  } finally {
    mcpConfigSaving.value = false
  }
}

// 退出 MCP 登录
const handleXhsMcpLogout = async (account) => {
  try {
    await ElMessageBox.confirm(`确认退出 ${account.name} 的小红书登录？`, '提示', {
      confirmButtonText: '确认退出', cancelButtonText: '取消', type: 'warning'
    })
    await fetch(`${account.url}/api/v1/login/cookies`, { method: 'DELETE' })
    ElMessage.success(`${account.name} 已退出登录`)
    refreshXhsMcpStatus()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('退出登录失败')
  }
}

// SSE连接状态
const sseConnecting = ref(false)
const qrCodeData = ref('')
const loginStatus = ref('')

// 添加账号
const handleAddAccount = () => {
  dialogType.value = 'add'
  Object.assign(accountForm, {
    id: null,
    name: '',
    platform: '',
    status: '正常'
  })
  // 重置SSE状态
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''
  dialogVisible.value = true
}

// 编辑账号
const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(accountForm, {
    id: row.id,
    name: row.name,
    platform: row.platform,
    status: row.status
  })
  dialogVisible.value = true
}

// 删除账号
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除账号 ${row.name} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // 调用API删除账号
        const response = await accountApi.deleteAccount(row.id)

        if (response.code === 200) {
          // 从状态管理中删除账号
          accountStore.deleteAccount(row.id)
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        } else {
          ElMessage.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除账号失败:', error)
        ElMessage.error('删除账号失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// 下载Cookie文件
const handleDownloadCookie = (row) => {
  // 从后端获取Cookie文件
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
  const downloadUrl = `${baseUrl}/downloadCookie?filePath=${encodeURIComponent(row.filePath)}`

  // 创建一个隐藏的链接来触发下载
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = `${row.name}_cookie.json`
  link.target = '_blank'
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 上传Cookie文件
const handleUploadCookie = (row) => {
  // 创建一个隐藏的文件输入框
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.style.display = 'none'
  document.body.appendChild(input)

  input.onchange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // 检查文件类型
    if (!file.name.endsWith('.json')) {
      ElMessage.error('请选择JSON格式的Cookie文件')
      document.body.removeChild(input)
      return
    }

    try {
      // 创建FormData对象
      const formData = new FormData()
      formData.append('file', file)
      formData.append('id', row.id)
      formData.append('platform', row.platform)

      // 使用统一的http封装发送上传请求
      const result = await http.upload('/uploadCookie', formData)

      ElMessage.success('Cookie文件上传成功')
      // 刷新账号列表以显示更新
      fetchAccounts()
    } catch (error) {
      ElMessage.error('Cookie文件上传失败')
    } finally {
      document.body.removeChild(input)
    }
  }

  input.click()
}

// 重新登录账号
const handleReLogin = (row) => {
  // 设置表单信息
  dialogType.value = 'edit'
  Object.assign(accountForm, {
    id: row.id,
    name: row.name,
    platform: row.platform,
    status: row.status
  })

  // 重置SSE状态
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''

  // 显示对话框
  dialogVisible.value = true

  // 立即开始登录流程
  setTimeout(() => {
    // 小红书走 MCP 登录
    if (row.platform === '小红书') {
      dialogVisible.value = false
      handleXhsMcpLogin(row.name)
      return
    }
    connectSSE(row.platform, row.name)
  }, 300)
}

// 获取默认头像
const getDefaultAvatar = (name) => {
  // 使用简单的默认头像，可以基于用户名生成不同的颜色
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`
}

// SSE事件源对象
let eventSource = null

// 关闭SSE连接
const closeSSEConnection = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

// 建立SSE连接
const connectSSE = (platform, name) => {
  // 关闭可能存在的连接
  closeSSEConnection()

  // 设置连接状态
  sseConnecting.value = true
  qrCodeData.value = ''
  loginStatus.value = ''

  // 获取平台类型编号
  const platformTypeMap = {
    '小红书': '1',
    '视频号': '2',
    '抖音': '3',
    '快手': '4'
  }

  const type = platformTypeMap[platform] || '1'

  // 创建SSE连接
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
  const url = `${baseUrl}/login?type=${type}&id=${encodeURIComponent(name)}`

  eventSource = new EventSource(url)

  // 监听消息
  eventSource.onmessage = (event) => {
    const data = event.data

    // 如果还没有二维码数据，且数据长度较长，认为是二维码
    if (!qrCodeData.value && data.length > 100) {
      try {
        if (data.startsWith('data:image')) {
          qrCodeData.value = data
        } else {
          qrCodeData.value = `data:image/png;base64,${data}`
        }
      } catch (error) {
        // 处理二维码数据出错
      }
    }
    // 如果收到状态码
    else if (data === '200' || data === '500') {
      loginStatus.value = data

      // 如果登录成功
      if (data === '200') {
        setTimeout(() => {
          // 关闭连接
          closeSSEConnection()

          // 1秒后关闭对话框并开始刷新
          setTimeout(() => {
            dialogVisible.value = false
            sseConnecting.value = false

            // 根据是否是重新登录显示不同提示
            ElMessage.success(dialogType.value === 'edit' ? '重新登录成功' : '账号添加成功')

            // 显示更新账号信息提示
            ElMessage({
              type: 'info',
              message: '正在同步账号信息...',
              duration: 0
            })

            // 触发刷新操作
            fetchAccounts().then(() => {
              // 刷新完成后关闭提示
              ElMessage.closeAll()
              ElMessage.success('账号信息已更新')
            })
          }, 1000)
        }, 1000)
      } else {
        // 登录失败，关闭连接
        closeSSEConnection()

        // 2秒后重置状态，允许重试
        setTimeout(() => {
          sseConnecting.value = false
          qrCodeData.value = ''
          loginStatus.value = ''
        }, 2000)
      }
    }
  }

  // 监听错误
  eventSource.onerror = (error) => {
    console.error('SSE连接错误:', error)
    ElMessage.error('连接服务器失败，请稍后再试')
    closeSSEConnection()
    sseConnecting.value = false
  }
}

// 提交账号表单
const submitAccountForm = () => {
  accountFormRef.value.validate(async (valid) => {
    if (valid) {
      if (dialogType.value === 'add') {
        // 小红书拦截：走 MCP 登录，不走旧 SSE
        if (accountForm.platform === '小红书') {
          dialogVisible.value = false
          handleXhsMcpLogin(accountForm.name || '')
          return
        }
        // 其他平台走 SSE 登录
        connectSSE(accountForm.platform, accountForm.name)
      } else {
        // 编辑账号逻辑
        try {
          // 将平台名称转换为类型数字
          const platformTypeMap = {
            '小红书': 1,
            '视频号': 2,
            '抖音': 3,
            '快手': 4
          };
          const type = platformTypeMap[accountForm.platform] || 1;

          const res = await accountApi.updateAccount({
            id: accountForm.id,
            type: type,
            userName: accountForm.name
          })
          if (res.code === 200) {
            // 更新状态管理中的账号
            const updatedAccount = {
              id: accountForm.id,
              name: accountForm.name,
              platform: accountForm.platform,
              status: accountForm.status // Keep the existing status
            };
            accountStore.updateAccount(accountForm.id, updatedAccount)
            ElMessage.success('更新成功')
            dialogVisible.value = false
            // 刷新账号列表
            fetchAccounts()
          } else {
            ElMessage.error(res.msg || '更新账号失败')
          }
        } catch (error) {
          console.error('更新账号失败:', error)
          ElMessage.error('更新账号失败')
        }
      }
    } else {
      return false
    }
  })
}

// 组件卸载前关闭SSE连接
onBeforeUnmount(() => {
  closeSSEConnection()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.account-management {
  .page-header {
    margin-bottom: 20px;
    
    h1 {
      font-size: 24px;
      color: $text-primary;
      margin: 0;
    }
  }
  
  .account-tabs {
    background-color: #fff;
    border-radius: 4px;
    box-shadow: $box-shadow-light;
    
    .account-tabs-nav {
      padding: 20px;
    }
  }
  
  .account-list-container {
    .account-search {
      display: flex;
      justify-content: space-between;
      margin-bottom: 20px;
      
      .el-input {
        width: 300px;
      }
      
      .action-buttons {
        display: flex;
        gap: 10px;
        
        .el-icon.is-loading {
          animation: rotate 1s linear infinite;
        }
      }
    }
    
    .account-list {
      margin-bottom: 20px;
    }
    
    .empty-data {
      padding: 40px 0;
    }
  }
  
  // 二维码容器样式
  .clickable-status {
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
    }
  }

  .qrcode-container {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 250px;
    
    .qrcode-wrapper {
      text-align: center;
      
      .qrcode-tip {
        margin-bottom: 15px;
        color: #606266;
      }
      
      .qrcode-image {
        max-width: 200px;
        max-height: 200px;
        border: 1px solid #ebeef5;
        background-color: black;
      }
    }
    
    .loading-wrapper, .success-wrapper, .error-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      
      .el-icon {
        font-size: 48px;
        
        &.is-loading {
          animation: rotate 1s linear infinite;
        }
      }
      
      span {
        font-size: 16px;
      }
    }
    
    .success-wrapper .el-icon {
      color: #67c23a;
    }
    
    .error-wrapper .el-icon {
      color: #f56c6c;
    }
  }
}
</style>