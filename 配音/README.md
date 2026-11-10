# 配音

用户本人ElevenLabs克隆音色的可复用项目与Codex Skill。已经确认的音色、模型和参数见 `voice-profile.json`。仓库不保存API密钥、真人录音或生成音频。

## 安装Skill

对Codex说：

> 从 https://github.com/mitang09151018-ux/codex/tree/main/配音/skills/my-voice 安装Skill。

安装后使用 `$my-voice`，并提供需要朗读的原稿。本Skill使用ElevenLabs云端API，需将 `ELEVENLABS_API_KEY` 配置到本机环境中。配置文件不包含密钥，不会授予其他人账户或音色访问权限。

## 独立调用

```bash
python3 skills/my-voice/scripts/synthesize.py --check
python3 skills/my-voice/scripts/synthesize.py --text-file /path/to/script.txt --output /path/to/narration.mp3 --timestamps
```

仅使用Python标准库； `--check` 不调用API、不消耗额度。合成会使用ElevenLabs账户额度。脚本不自动重试未知结果的请求，也不覆盖已有文件。

默认名称“我自己的音色”，模型 `eleven_multilingual_v2`。原稿默认保持不变。音色保存在ElevenLabs账户，不能通过本仓库导出为离线模型。本地离线模式尚未配置，需要原始真人录音及另一个本地语音模型。

`voice-profile.json` 是项目参数；Skill中的 `references/voice-profile.json` 是独立安装所需的同一份配置副本，修改参数时同步两份。
