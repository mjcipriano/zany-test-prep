import 'dart:convert';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/backup.dart';

/// Export/import of all local progress so it can move between devices or survive
/// a reinstall. Backups are portable JSON files, validated and version-aware on
/// import (see [decodeBackup]).
class BackupScreen extends ConsumerWidget {
  const BackupScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Backup & restore')),
      body: ListView(
        padding: kPagePadding,
        children: [
          AppCard(
            color: scheme.primaryContainer,
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Move your progress between devices',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
                Gap.s,
                Text(
                  'Export a backup file and keep it somewhere safe (cloud drive, '
                  'email, etc.). On another device — or after reinstalling — import '
                  'it to restore your XP, streaks, mastery, settings, and unlocks. '
                  'Backups are cross-platform and version-aware.',
                  style: TextStyle(height: 1.4),
                ),
              ],
            ),
          ),
          Gap.l,
          const SectionLabel('Export'),
          AppCard(
            child: Column(
              children: [
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.ios_share_rounded),
                  title: const Text('Share backup file'),
                  subtitle: const Text(
                    'Send to another device or save to a drive',
                  ),
                  onTap: () => _shareBackup(context, ref),
                ),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.copy_rounded),
                  title: const Text('Copy backup to clipboard'),
                  subtitle: const Text('Paste it anywhere to save or transfer'),
                  onTap: () => _copyBackup(context, ref),
                ),
              ],
            ),
          ),
          Gap.l,
          const SectionLabel('Import'),
          AppCard(
            child: Column(
              children: [
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.folder_open_rounded),
                  title: const Text('Import from file'),
                  subtitle: const Text('Choose a backup file to restore'),
                  onTap: () => _importFromFile(context, ref),
                ),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.content_paste_rounded),
                  title: const Text('Import from clipboard'),
                  subtitle: const Text('Paste a backup you copied earlier'),
                  onTap: () => _importFromClipboard(context, ref),
                ),
              ],
            ),
          ),
          Gap.m,
          Text(
            'Importing replaces all progress currently on this device.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  // --- Export ---

  Future<void> _shareBackup(BuildContext context, WidgetRef ref) async {
    final content = ref.read(appControllerProvider.notifier).exportBackup();
    try {
      final dir = await getTemporaryDirectory();
      final stamp = DateTime.now().toIso8601String().split('T').first;
      final file = File('${dir.path}/zany-test-prep-backup-$stamp.json');
      await file.writeAsString(content);
      await Share.shareXFiles([
        XFile(file.path, mimeType: 'application/json'),
      ], subject: 'Zany Test Prep backup');
    } catch (e) {
      if (context.mounted) _snack(context, "Couldn't share the backup: $e");
    }
  }

  Future<void> _copyBackup(BuildContext context, WidgetRef ref) async {
    final content = ref.read(appControllerProvider.notifier).exportBackup();
    await Clipboard.setData(ClipboardData(text: content));
    if (context.mounted) _snack(context, 'Backup copied to clipboard');
  }

  // --- Import ---

  Future<void> _importFromFile(BuildContext context, WidgetRef ref) async {
    String? raw;
    try {
      final result = await FilePicker.platform.pickFiles(withData: true);
      if (result == null) return; // cancelled
      final picked = result.files.single;
      if (picked.bytes != null) {
        raw = utf8.decode(picked.bytes!, allowMalformed: true);
      } else if (picked.path != null) {
        raw = await File(picked.path!).readAsString();
      }
    } catch (e) {
      if (context.mounted) _snack(context, "Couldn't read that file: $e");
      return;
    }
    if (raw == null) {
      if (context.mounted) _snack(context, 'No file selected.');
      return;
    }
    if (context.mounted) await _confirmAndImport(context, ref, raw);
  }

  Future<void> _importFromClipboard(BuildContext context, WidgetRef ref) async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    final raw = data?.text ?? '';
    if (context.mounted) await _confirmAndImport(context, ref, raw);
  }

  Future<void> _confirmAndImport(
    BuildContext context,
    WidgetRef ref,
    String raw,
  ) async {
    final parse = ref.read(appControllerProvider.notifier).parseBackup(raw);
    if (!parse.ok) {
      _snack(context, parse.message);
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => _ConfirmImportDialog(parse: parse),
    );
    if (confirmed != true || !context.mounted) return;
    await ref.read(appControllerProvider.notifier).importBackup(parse.data!);
    if (context.mounted) _snack(context, 'Progress imported ✅');
  }

  void _snack(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }
}

class _ConfirmImportDialog extends StatelessWidget {
  const _ConfirmImportDialog({required this.parse});
  final BackupParse parse;

  @override
  Widget build(BuildContext context) {
    final s = parse.summary!;
    final exported = s.exportedAt == null
        ? null
        : '${s.exportedAt!.year}-${s.exportedAt!.month.toString().padLeft(2, '0')}-${s.exportedAt!.day.toString().padLeft(2, '0')}';
    return AlertDialog(
      title: const Text('Import this backup?'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _row('Total XP', '${s.totalXp}'),
          _row('Current streak', '${s.currentStreak}'),
          _row('Lessons completed', '${s.lessonsCompleted}'),
          _row('Unlocked items', '${s.ownedAssets}'),
          if (s.appVersion != null) _row('From app', s.appVersion!),
          if (exported != null) _row('Exported', exported),
          Gap.m,
          const Text(
            'This replaces all progress currently on this device.',
            style: TextStyle(fontWeight: FontWeight.w700),
          ),
          if (parse.warnings.isNotEmpty) ...[
            Gap.s,
            ...parse.warnings.map(
              (w) => Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.warning_amber_rounded,
                      size: 16,
                      color: AppTheme.streak,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        w,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(false),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(true),
          child: const Text('Import'),
        ),
      ],
    );
  }

  Widget _row(String label, String value) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 2),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w700)),
      ],
    ),
  );
}
