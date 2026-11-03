<template>
  <div>
    <h2 class="mb-4">{{ $t('plugin_llama_swap.title') }}</h2>

    <v-skeleton-loader v-if="loading" :loading="true" type="card" />

    <div v-else style="margin-bottom: 80px">
      <!-- Status Card -->
      <v-card class="mb-4 pa-0">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-backup-restore</v-icon>
          <span>{{ $t('plugin_llama_swap.status') }}</span>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <span class="text-subtitle-1 font-weight-medium">
                {{ $t('plugin_llama_swap.version') }} {{ currentVersion || $t('plugin_llama_swap.not_installed') }}
              </span>
            </v-col>
            <v-col cols="12" md="3">
              <span class="text-subtitle-1 font-weight-medium">
                {{ $t('plugin_llama_swap.latest_version') }} {{ latestVersion || '-' }}
              </span>
            </v-col>
            <v-col cols="12" md="3">
              <span class="text-subtitle-1 font-weight-medium">
                {{ $t('plugin_llama_swap.status') }}: {{ running ? $t('plugin_llama_swap.running') : $t('plugin_llama_swap.not_running') }}
              </span>
            </v-col>
            <v-col cols="12" md="auto" class="d-flex ga-2 flex-nowrap flex-md-row">
              <v-btn size="small" variant="tonal" color="secondary" @click="checkForUpdates" :loading="checkingUpdates">
                {{ $t('plugin_llama_swap.check_updates') }}
              </v-btn>
              <v-btn
                v-if="!currentVersion && installPathSaved && settings.install_path"
                size="small" variant="tonal" color="primary"
                @click="doInstall" :loading="installing"
              >
                {{ $t('plugin_llama_swap.install') }}
              </v-btn>
              <v-btn
                v-else-if="currentVersion && updateAvailable"
                size="small" variant="tonal" color="primary"
                @click="doUpdate" :loading="updating"
              >
                {{ $t('plugin_llama_swap.update') }}
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Persistent llama.cpp backend -->
      <v-card class="mb-4 pa-0">
        <v-card-title class="d-flex align-center"><v-icon class="mr-2">mdi-chip</v-icon>llama.cpp Backend</v-card-title>
        <v-card-text>
          <div class="mb-2">{{ backendStatus.installed ? 'Installed' : 'Not installed' }} · {{ backendStatus.version || 'No version' }} · {{ backendStatus.backend || 'Backend not selected' }}</div>
          <div class="text-caption mb-3">{{ backendStatus.binary || 'Choose a persistent install path and save settings first.' }}</div>
          <v-btn class="mr-2 mb-2" size="small" variant="tonal" :loading="backendBusy" :disabled="!installPathSaved" @click="backendAction('status')">Refresh backend</v-btn>
          <v-btn class="mr-2 mb-2" size="small" variant="tonal" :loading="backendBusy" :disabled="!installPathSaved" @click="backendAction('stage_vulkan')">Stage Vulkan packages</v-btn>
          <v-btn class="mb-2" size="small" color="primary" :loading="backendBusy" :disabled="!installPathSaved" @click="backendAction('install')">Install / update llama.cpp</v-btn>
          <div v-if="backendMessage" class="text-caption mt-2" style="white-space: pre-wrap">{{ backendMessage }}</div>
        </v-card-text>
      </v-card>

      <!-- Settings Card -->
      <v-card class="mb-4 pa-0">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-harddisk</v-icon>
          <span>{{ $t('plugin_llama_swap.settings') }}</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="settings.install_path" :label="$t('plugin_llama_swap.install_path')">
            <template #append-inner>
              <v-btn size="small" icon="mdi-folder" @click="openFsDialog" variant="text" />
            </template>
          </v-text-field>
          <div v-if="!installPathSaved" class="text-subtitle-2 text-warning mt-2">
            {{ $t('plugin_llama_swap.no_path_set') }}{{ recommendedPath ? ' ' + recommendedPath : '' }}
          </div>
          <template v-if="installPathSaved">
            <v-divider class="my-4" />
            <v-text-field
              v-model="settings.port"
              :label="$t('plugin_llama_swap.port')"
              :hint="$t('plugin_llama_swap.default_port_hint', { port: 8081 })"
              persistent-hint
              :rules="portRules"
              type="number"
              style="max-width: 200px"
            />
            <v-switch
              v-model="settings.auto_start"
              :label="$t('plugin_llama_swap.auto_start')"
              inset color="green" hide-details
              class="mt-2"
            />
          </template>
          <v-btn color="primary" class="mt-4" @click="saveSettings" :loading="saving">
            <v-icon start>mdi-content-save</v-icon>
            {{ $t('plugin_llama_swap.save_settings') }}
          </v-btn>
        </v-card-text>
      </v-card>

      <!-- Start/Stop Card -->
      <v-card v-if="installPathSaved && configSaved" class="mb-4 pa-0">
        <v-card-text class="d-flex align-center ga-2">
          <v-btn color="primary" rounded :loading="starting" @click="startDaemon">
            <v-icon start>mdi-play</v-icon>
            {{ $t('plugin_llama_swap.start') }}
          </v-btn>
          <v-btn color="error" rounded variant="outlined" :loading="stopping" @click="stopDaemon">
            <v-icon start>mdi-stop</v-icon>
            {{ $t('plugin_llama_swap.stop') }}
          </v-btn>
          <v-btn
            v-if="running"
            color="secondary" rounded variant="tonal"
            :href="webuiUrl" target="_blank"
          >
            <v-icon start>mdi-open-in-new</v-icon>
            {{ $t('plugin_llama_swap.open_webui') }}
          </v-btn>
        </v-card-text>
      </v-card>

      <!-- Config Card -->
      <v-card v-if="installPathSaved" class="mb-4 pa-0">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-folder</v-icon>
          <span>{{ $t('plugin_llama_swap.config') }}</span>
        </v-card-title>
        <v-card-text>
          <div v-if="!configSaved" class="text-subtitle-2 text-warning mb-3">
            {{ $t('plugin_llama_swap.config_not_saved') }}
          </div>
          <v-textarea
            v-model="configContent"
            :loading="loadingConfig"
            :rows="15"
            hide-details
            style="font-family: monospace"
          />
          <v-btn color="primary" class="mt-4" @click="confirmSaveConfig" :loading="savingConfig">
            <v-icon start>mdi-content-save</v-icon>
            {{ $t('plugin_llama_swap.save_config') }}
          </v-btn>
        </v-card-text>
      </v-card>
    </div>

    <!-- Restart Confirmation Dialog -->
    <v-dialog v-model="restartDialog" max-width="400">
      <v-card :title="$t('plugin_llama_swap.restart_required')" prepend-icon="mdi-restart" class="pa-0">
        <v-card-text>
          {{ $t('plugin_llama_swap.restart_confirm_message') }}
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-row class="d-flex justify-end">
            <v-btn color="onPrimary" @click="restartDialog = false">{{ $t('plugin_llama_swap.cancel') }}</v-btn>
            <v-btn color="primary" @click="restartDialog = false; saveConfig()">{{ $t('plugin_llama_swap.ok') }}</v-btn>
          </v-row>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Overlay -->
    <v-overlay :model-value="overlay" class="align-center justify-center">
      <v-progress-circular color="onPrimary" size="64" indeterminate />
    </v-overlay>

    <!-- File System Dialog -->
    <v-dialog v-model="fsDialog" max-width="800">
      <v-card>
        <v-card-title class="d-flex align-center">
          <span>{{ $t('plugin_llama_swap.select_directory') }}</span>
          <v-spacer />
          <v-chip size="small" class="ml-2" variant="tonal">{{ fsCurrentPath || '/' }}</v-chip>
        </v-card-title>
        <v-card-subtitle class="pb-0">
          <div class="d-flex align-center ga-2">
            <v-btn size="small" variant="text" icon="mdi-home" @click="fsGoRoot" color="secondary" :disabled="fsLoading" />
            <v-btn size="small" variant="text" icon="mdi-arrow-up" @click="fsNavigateUp" color="secondary" :disabled="fsCurrentPath === '/mnt' || fsLoading" />
            <v-btn size="small" variant="text" icon="mdi-refresh" @click="fetchDirectory(fsCurrentPath)" color="secondary" :disabled="fsLoading" />
            <v-spacer />
            <v-progress-circular v-if="fsLoading" indeterminate size="20" color="secondary" />
          </div>
        </v-card-subtitle>
        <v-card-text class="pt-2" style="min-height: 300px; max-height: 60vh; overflow-y: auto">
          <v-table density="compact">
            <thead>
              <tr>
                <th>{{ $t('plugin_llama_swap.name') }}</th>
                <th style="width: 40%">{{ $t('plugin_llama_swap.path') }}</th>
                <th style="width: 60px" class="text-center">{{ $t('plugin_llama_swap.action') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!fsLoading && fsItems.length === 0">
                <td colspan="3" class="text-center text-medium-emphasis">{{ $t('plugin_llama_swap.no_entries') }}</td>
              </tr>
              <tr
                v-for="item in fsItems"
                :key="item.path"
                :class="['cursor-pointer', fsActiveItem && fsActiveItem.path === item.path ? 'bg-primary bg-opacity-10' : '']"
                @click="fsActiveItem = item"
                @dblclick.stop.prevent="fsNavigateInto(item)"
              >
                <td>
                  <div class="d-flex align-center ga-2">
                    <v-icon size="18">mdi-folder</v-icon>
                    <span>{{ item.name }}</span>
                  </div>
                </td>
                <td><span class="text-caption">{{ item.displayPath || item.path }}</span></td>
                <td class="text-center">
                  <v-btn size="small" icon="mdi-folder-open" variant="text" @click.stop="fsNavigateInto(item)" :disabled="fsLoading" />
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider />
        <v-card-actions class="d-flex align-center">
          <div class="text-caption text-truncate" style="max-width: 60%">
            <strong>{{ $t('plugin_llama_swap.selected') }}:</strong>
            <span v-if="fsActiveItem">{{ fsActiveItem.displayPath || fsActiveItem.path }}</span>
            <span v-else>-</span>
          </div>
          <v-spacer />
          <v-btn variant="text" color="onPrimary" @click="fsDialog = false">{{ $t('plugin_llama_swap.cancel') }}</v-btn>
          <v-btn color="onPrimary" @click="fsSelect" :disabled="fsLoading">{{ $t('plugin_llama_swap.select') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, getCurrentInstance, onMounted, onUnmounted } from 'vue';

const PLUGIN_NAME = 'llama';
const backendStatus = reactive({ installed: false, version: '', backend: '', binary: '' });
const backendBusy = ref(false);
const backendMessage = ref('');
const refreshBackendStatus = async () => {
  const res = await fetch('/api/v1/mos/plugins/query', {
    method: 'POST',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: 'llama_backend', args: ['status'], timeout: 15, parse_json: true }),
  });
  const data = await res.json();
  if (!res.ok || data.success !== true) throw new Error(data.error || 'Status refresh failed');
  Object.assign(backendStatus, typeof data.output === 'string' ? JSON.parse(data.output) : data.output);
};
const backendAction = async (action) => {
  if (!installPathSaved.value) return;
  backendBusy.value = true;
  backendMessage.value = '';
  try {
    const res = await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command: 'llama_backend', args: [action],
        timeout: action === 'status' ? 15 : 300,
        parse_json: action === 'status',
      }),
    });
    const data = await res.json();
    if (!res.ok || data.success !== true) {
      throw new Error(data.error || data.output || `Backend operation failed (${res.status})`);
    }
    if (action === 'status') {
      const result = typeof data.output === 'string' ? JSON.parse(data.output) : data.output;
      if (!result || typeof result !== 'object') throw new Error('Unexpected backend status response');
      Object.assign(backendStatus, result);
    } else {
      backendMessage.value = typeof data.output === 'string' ? data.output : JSON.stringify(data.output);
      refreshBackendStatus().catch(() => {});
    }
  } catch (e) {
    backendMessage.value = String(e.message || e);
  } finally {
    backendBusy.value = false;
  }
};

const t = (key) => getCurrentInstance()?.appContext.config.globalProperties.$t(key) ?? key;

const loading = ref(true);
const saving = ref(false);
const savingConfig = ref(false);
const overlay = ref(false);
const starting = ref(false);
const stopping = ref(false);
const checkingUpdates = ref(false);
const updating = ref(false);
const installing = ref(false);
const loadingConfig = ref(false);
const fsDialog = ref(false);
const fsCurrentPath = ref('');
const fsItems = ref([]);
const fsLoading = ref(false);
const fsActiveItem = ref(null);
const statusInterval = ref(null);

const running = ref(false);
const currentVersion = ref('');
const latestVersion = ref('');
const updateAvailable = ref(false);
const configContent = ref('');

const settings = reactive({
  install_path: '',
  auto_start: false,
  port: '8081',
  version: ''
});

const DEFAULT_PORT = '8081';

const portRules = [
  (v) => {
    const port = parseInt(v, 10);
    return (Number.isInteger(port) && port >= 1 && port <= 65535) || t('plugin_llama_swap.port_invalid');
  },
];

const webuiUrl = computed(() => {
  const port = settings.port || DEFAULT_PORT;
  return `${window.location.protocol}//${window.location.hostname}:${port}`;
});

const installPathSaved = ref(false);
const recommendedPath = ref('');
const configSaved = ref(true);
const restartDialog = ref(false);

const getAuthHeaders = () => ({
  Authorization: 'Bearer ' + localStorage.getItem('authToken'),
});

const getInstallPath = async () => {
  let path = settings.install_path;
  if (!path) {
    try {
      const res = await fetch('/api/v1/mos/settings/docker', {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.appdata) {
          path = data.appdata + '/llama';
        }
      }
    } catch (e) {
      console.error('Failed to fetch docker settings:', e);
    }
  }
  return path;
};

const doInstall = async () => {
  installing.value = true;
  try {
    const installPath = settings.install_path;

    if (!installPath) {
      alert('Error: Install path not set. Please set install path and save first.');
      installing.value = false;
      return;
    }

    await fetch(`/api/v1/mos/plugins/settings/${PLUGIN_NAME}`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        install_path: installPath,
        auto_start: settings.auto_start,
        port: normalizePort(),
        version: '',
      }),
    });

    installPathSaved.value = true;
    recommendedPath.value = '';
    currentVersion.value = '';

    const res = await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: 'llama_router',
        args: ['install_binary'],
        timeout: 120,
        parse_json: false,
      }),
    });

    if (!res.ok) {
      throw new Error('Install failed');
    }

    await fetchSettings();
    await checkStatus();
    await checkForUpdates();
  } catch (e) {
    console.error('Failed to install:', e);
    alert('Failed to install llama-swap. Check logs for details.');
  } finally {
    installing.value = false;
  }
};

const doUpdate = async () => {
  updating.value = true;
  try {
    if (running.value) {
      await fetch('/api/v1/mos/plugins/query', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: 'llama_router',
          args: ['stop'],
          timeout: 30,
          parse_json: false,
        }),
      });
    }

    const res = await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: 'llama_router',
        args: ['install_binary'],
        timeout: 120,
        parse_json: false,
      }),
    });

    if (!res.ok) {
      throw new Error('Update failed');
    }

    if (running.value) {
      await fetch('/api/v1/mos/plugins/query', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: 'llama_router',
          args: ['start'],
          timeout: 30,
          parse_json: false,
        }),
      });
    }

    await fetchSettings();
    await checkStatus();
    await checkForUpdates();
  } catch (e) {
    console.error('Failed to update:', e);
    alert('Failed to update llama-swap. Check logs for details.');
  } finally {
    updating.value = false;
  }
};

const openFsDialog = async () => {
  fsCurrentPath.value = settings.install_path || '/mnt';
  fsDialog.value = true;
  await fetchDirectory(fsCurrentPath.value);
};

const fetchDirectory = async (dirPath) => {
  fsLoading.value = true;
  fsActiveItem.value = null;
  try {
    const url = new URL('/api/v1/mos/fsnavigator', window.location.origin);
    if (dirPath && dirPath !== '/') {
      url.searchParams.set('path', dirPath);
    }
    url.searchParams.set('type', 'directories');
    url.searchParams.set('roots', '/mnt');

    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });

    if (res.ok) {
      const data = await res.json();
      fsCurrentPath.value = data.currentPath || dirPath || '/mnt';
      fsItems.value = Array.isArray(data.items) ? data.items : [];
    } else {
      fsItems.value = [];
    }
  } catch (e) {
    console.error('Failed to fetch directory:', e);
    fsItems.value = [];
  } finally {
    fsLoading.value = false;
  }
};

const fsNavigateInto = (item) => {
  if (!item || item.type !== 'directory') return;
  fetchDirectory(item.path);
};

const fsNavigateUp = () => {
  if (!fsCurrentPath.value || fsCurrentPath.value === '/mnt') return;
  const parts = fsCurrentPath.value.split('/').filter(Boolean);
  parts.pop();
  const parentPath = '/' + parts.join('/');
  fetchDirectory(parentPath || '/mnt');
};

const fsGoRoot = () => {
  fetchDirectory('/mnt');
};

const fsSelect = () => {
  if (fsActiveItem.value) {
    settings.install_path = fsActiveItem.value.path;
  } else {
    settings.install_path = fsCurrentPath.value;
  }
  fsDialog.value = false;
};

const fetchSettings = async () => {
  try {
    const res = await fetch(`/api/v1/mos/plugins/settings/${PLUGIN_NAME}`, {
      headers: getAuthHeaders(),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.install_path !== undefined && data.install_path) {
        settings.install_path = data.install_path;
        installPathSaved.value = true;
        recommendedPath.value = '';
        console.log('Path saved, installPathSaved=true');
      } else {
        settings.install_path = '';
        installPathSaved.value = false;
        console.log('No path, installPathSaved=false');
      }
      if (data.auto_start !== undefined) {
        settings.auto_start = data.auto_start;
      }
      if (data.port !== undefined && data.port !== null && String(data.port) !== '' && String(data.port) !== '0') {
        settings.port = String(data.port);
      } else {
        settings.port = DEFAULT_PORT;
      }
      if (data.version) {
        currentVersion.value = data.version;
      }
    }

    if (!installPathSaved.value && !settings.install_path) {
      try {
        const dockerRes = await fetch('/api/v1/mos/settings/docker', {
          headers: getAuthHeaders(),
        });
        if (dockerRes.ok) {
          const dockerData = await dockerRes.json();
          if (dockerData.appdata) {
            recommendedPath.value = dockerData.appdata + '/llama-swap';
          }
        }
      } catch (e) {
        console.error('Failed to fetch docker settings:', e);
      }
    }
  } catch (e) {
    console.error('Failed to fetch settings:', e);
  }
};

const fetchConfig = async () => {
  loadingConfig.value = true;
  try {
    const installPath = await getInstallPath();
    if (installPath) {
      const url = new URL('/api/v1/mos/readfile', window.location.origin);
      url.searchParams.set('path', installPath + '/llama-swap.config');

      const fileRes = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (fileRes.ok) {
        const fileData = await fileRes.json();
        configContent.value = fileData.content || '';
        configSaved.value = true;
      } else {
        configContent.value = '# llama-swap configuration\n# Edit this file to configure your models\n';
        configSaved.value = false;
      }
    }
  } catch (e) {
    console.error('Failed to fetch config:', e);
    configContent.value = '# llama-swap configuration\n# Edit this file to configure your models\n';
  } finally {
    loadingConfig.value = false;
  }
};

const checkStatus = async () => {
  try {
    const res = await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: 'llama_router',
        args: ['status'],
        timeout: 5,
        parse_json: true,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success && data.output) {
        running.value = data.output.running === true;
      }
    }
  } catch (e) {
    running.value = false;
  }
};

const checkForUpdates = async () => {
  checkingUpdates.value = true;
  try {
    const res = await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: 'llama_router',
        args: ['check_version'],
        timeout: 15,
        parse_json: true,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success && data.output) {
        latestVersion.value = data.output.latest || '';
        updateAvailable.value = currentVersion.value && data.output.update_available === true;
      }
    }
  } catch (e) {
    console.error('Failed to check updates:', e);
  } finally {
    checkingUpdates.value = false;
  }
};

const startDaemon = async () => {
  starting.value = true;
  try {
    await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: 'llama_router',
        args: ['start'],
        timeout: 30,
        parse_json: false,
      }),
    });
    await checkStatus();
  } catch (e) {
    console.error('Failed to start:', e);
  } finally {
    starting.value = false;
  }
};

const stopDaemon = async () => {
  stopping.value = true;
  try {
    await fetch('/api/v1/mos/plugins/query', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: 'llama_router',
        args: ['stop'],
        timeout: 30,
        parse_json: false,
      }),
    });
    await checkStatus();
  } catch (e) {
    console.error('Failed to stop:', e);
  } finally {
    stopping.value = false;
  }
};

const normalizePort = () => {
  const port = parseInt(settings.port, 10);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    settings.port = DEFAULT_PORT;
  } else {
    settings.port = String(port);
  }
  return settings.port;
};

const saveSettings = async () => {
  saving.value = true;
  try {
    const port = normalizePort();
    await fetch(`/api/v1/mos/plugins/settings/${PLUGIN_NAME}`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        install_path: settings.install_path,
        auto_start: settings.auto_start,
        port,
        version: currentVersion.value,
      }),
    });
    installPathSaved.value = true;
    recommendedPath.value = '';
  } catch (e) {
    console.error('Failed to save settings:', e);
  } finally {
    saving.value = false;
  }
};

const confirmSaveConfig = () => {
  if (running.value) {
    restartDialog.value = true;
    return;
  }
  saveConfig();
};

const saveConfig = async () => {
  savingConfig.value = true;
  const wasRunning = running.value;
  try {
    if (wasRunning) {
      await fetch('/api/v1/mos/plugins/query', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: 'llama_router',
          args: ['stop'],
          timeout: 30,
          parse_json: false,
        }),
      });
    }

    const installPath = await getInstallPath();
    if (installPath) {
      const filePath = installPath + '/llama-swap.config';
      const editRes = await fetch('/api/v1/mos/editfile', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: filePath,
          content: configContent.value,
          create_backup: false,
        }),
      });
      if (!editRes.ok && editRes.status === 404) {
        await fetch('/api/v1/mos/createfile', {
          method: 'POST',
          headers: {
            ...getAuthHeaders(),
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            path: filePath,
            content: configContent.value,
          }),
        });
      }
    }

    if (wasRunning) {
      await fetch('/api/v1/mos/plugins/query', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: 'llama_router',
          args: ['start'],
          timeout: 30,
          parse_json: false,
        }),
      });
    }

    await checkStatus();
    configSaved.value = true;
  } catch (e) {
    console.error('Failed to save config:', e);
  } finally {
    savingConfig.value = false;
  }
};

onMounted(async () => {
  try {
    await fetchSettings();
    await fetchConfig();
    await checkStatus();
    if (installPathSaved.value) await backendAction('status');
    if (!currentVersion.value) {
      checkForUpdates();
    }

    statusInterval.value = setInterval(async () => {
      await checkStatus();
    }, 5000);
  } catch (e) {
    console.error('Failed to initialize:', e);
  } finally {
    loading.value = false;
  }
});

onUnmounted(() => {
  if (statusInterval.value) {
    clearInterval(statusInterval.value);
  }
});
</script>
