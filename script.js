// 选项卡功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化选项卡
    initTabs();
    
    // 初始化反馈表单
    initFeedbackForm();
    
    // 初始化资源中心
    initResourceCenter();
    
    // 初始化资源申请功能
    initResourceRequest();
});

// 选项卡切换
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有按钮和内容的active类
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // 添加active类到当前按钮和内容
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// 反馈表单功能
function initFeedbackForm() {
    const form = document.getElementById('feedbackForm');
    const textarea = document.getElementById('ideaContent');
    const charCount = document.getElementById('charCount');
    const submitBtn = document.getElementById('submitBtn');
    const buttonText = submitBtn.querySelector('.button-text');
    const loadingSpinner = submitBtn.querySelector('.loading-spinner');
    
    // 字符计数
    textarea.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count > 900) {
            charCount.style.color = '#ef4444';
        } else if (count > 700) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#6b7280';
        }
    });
    
    // 表单提交
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const content = textarea.value.trim();
        
        // 简单验证
        if (!content) {
            alert('请先填写一些内容再提交哦！');
            return;
        }
        
        // 显示加载状态
        buttonText.textContent = '提交中...';
        loadingSpinner.style.display = 'inline';
        submitBtn.disabled = true;
        
        // 隐藏之前的消息
        hideAllMessages();
        
        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    content: content,
                    type: 'feedback'
                })
            });

            if (response.ok) {
                showMessage('successMessage');
                textarea.value = '';
                charCount.textContent = '0';
                charCount.style.color = '#6b7280';
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || '提交失败');
            }
        } catch (error) {
            console.error('提交出错:', error);
            showMessage('errorMessage');
        } finally {
            // 恢复按钮状态
            buttonText.textContent = '提交灵感';
            loadingSpinner.style.display = 'none';
            submitBtn.disabled = false;
        }
    });
}

// 资源中心功能
function initResourceCenter() {
    const searchInput = document.getElementById('resourceSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    
    // 加载资源列表
    loadResources();
    
    // 搜索功能
    searchInput.addEventListener('input', filterResources);
    
    // 分类筛选
    categoryFilter.addEventListener('change', filterResources);
}

// 加载资源列表
async function loadResources() {
    const resourceList = document.getElementById('resourceList');
    
    try {
        // 尝试从API获取资源
        const response = await fetch('/api/resources');
        let resources = [];
        
        if (response.ok) {
            resources = await response.json();
        } else {
            // 如果API不可用，尝试从本地JSON文件加载
            const localResponse = await fetch('/data/resources.json');
            if (localResponse.ok) {
                resources = await localResponse.json();
            } else {
                throw new Error('无法加载资源列表');
            }
        }
        
        displayResources(resources);
        
    } catch (error) {
        console.error('加载资源失败:', error);
        resourceList.innerHTML = `
            <div class="message">
                <p>❌ 资源加载失败，请刷新页面重试</p>
            </div>
        `;
    }
}

// 显示资源列表
function displayResources(resources) {
    const resourceList = document.getElementById('resourceList');
    
    if (resources.length === 0) {
        resourceList.innerHTML = `
            <div class="message">
                <p>暂无资源，请稍后再来</p>
            </div>
        `;
        return;
    }
    
    resourceList.innerHTML = resources.map(resource => `
        <div class="resource-item" data-category="${resource.category}" data-title="${resource.title.toLowerCase()}">
            <div class="resource-icon">${resource.icon || '📄'}</div>
            <div class="resource-content">
                <div class="resource-title">${resource.title}</div>
                <div class="resource-description">${resource.description}</div>
                <div class="resource-meta">
                    <span class="resource-category">${resource.category}</span>
                    <span class="resource-size">${resource.fileSize}</span>
                </div>
            </div>
            <div class="resource-action">
                <a href="${resource.link}" target="_blank" class="download-button">下载</a>
            </div>
        </div>
    `).join('');
}

// 筛选资源
function filterResources() {
    const searchTerm = document.getElementById('resourceSearch').value.toLowerCase();
    const category = document.getElementById('categoryFilter').value;
    const resources = document.querySelectorAll('.resource-item');
    
    resources.forEach(resource => {
        const title = resource.getAttribute('data-title');
        const resourceCategory = resource.getAttribute('data-category');
        
        const matchesSearch = title.includes(searchTerm);
        const matchesCategory = !category || resourceCategory === category;
        
        if (matchesSearch && matchesCategory) {
            resource.style.display = 'flex';
        } else {
            resource.style.display = 'none';
        }
    });
}

// 资源申请功能
function initResourceRequest() {
    const requestLink = document.getElementById('requestResource');
    
    requestLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        const resourceName = prompt('请输入你需要的资源名称：');
        if (resourceName) {
            // 切换到反馈选项卡并预填内容
            document.querySelector('[data-tab="feedback"]').click();
            document.getElementById('ideaContent').value = `资源申请：${resourceName}\n\n申请理由：`;
            document.getElementById('ideaContent').focus();
            
            // 滚动到文本框
            document.getElementById('ideaContent').scrollIntoView({ 
                behavior: 'smooth' 
            });
        }
    });
}

// 工具函数
function hideAllMessages() {
    document.getElementById('successMessage').classList.add('hidden');
    document.getElementById('errorMessage').classList.add('hidden');
}

function showMessage(messageId) {
    hideAllMessages();
    document.getElementById(messageId).classList.remove('hidden');
}