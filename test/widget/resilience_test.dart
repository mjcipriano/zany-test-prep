import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/backup.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

import '../helpers/pump_app.dart';

void main() {
  testWidgets('a corrupt profile with the onboarded flag set re-onboards', (
    tester,
  ) async {
    // Regression: the router allowed /home, which spun forever without a
    // profile and offered no way out.
    final store = MemoryStore();
    store.setString('onboarded.v1', 'true');
    store.setString('profile.v1', '{not json');
    await pumpApp(tester, store: store);
    expect(find.text('Welcome to Zany Test Prep'), findsOneWidget);
  });

  test(
    'importing a backup for an exam this build lacks keeps the session usable',
    () async {
      final store = MemoryStore();
      final container = ProviderContainer(overrides: testOverrides(store));
      addTearDown(container.dispose);
      final controller = container.read(appControllerProvider.notifier);
      await container.read(appControllerProvider.future);
      await controller.completeOnboarding(examId: 'sat', dailyGoalMinutes: 10);

      final progress = AppProgress()..game.totalXp = 1234;
      await controller.importBackup(
        BackupData(
          profile: UserProfile.initial('psat-nope', 15),
          progress: progress,
          onboarded: true,
        ),
      );
      final data = container.read(appControllerProvider).requireValue;
      expect(data.bundle.exam.id, 'sat');
      expect(data.profile!.examId, 'sat');
      expect(data.profile!.dailyGoalMinutes, 15);
      expect(data.progress.game.totalXp, 1234);
      expect(data.onboarded, isTrue);
      final stored = jsonDecode(store.getString('profile.v1')!) as Map;
      expect(stored['examId'], 'sat');
    },
  );

  test('a backup without a profile is not treated as onboarded', () async {
    final store = MemoryStore();
    final container = ProviderContainer(overrides: testOverrides(store));
    addTearDown(container.dispose);
    final controller = container.read(appControllerProvider.notifier);
    await container.read(appControllerProvider.future);
    await controller.importBackup(
      BackupData(profile: null, progress: AppProgress(), onboarded: true),
    );
    expect(
      container.read(appControllerProvider).requireValue.onboarded,
      isFalse,
    );
  });
}
