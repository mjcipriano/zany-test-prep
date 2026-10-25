import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/notifications/reminder_scheduler.dart';
import '../domain/services/reminder_planner.dart';
import 'app_controller.dart';

/// Opens the route carried by a tapped reminder notification.
///
/// - Cold start (the tap launched the app): goes to the reminder's route
///   (Home, or Quick Practice for the streak nudge) once the app is up.
/// - Warm tap: only navigates when the player is on Home, so a reminder can
///   never yank them out of a lesson in progress.
///
/// Only routes in [kReminderRoutes] are honoured.
class NotificationRouteHandler extends ConsumerStatefulWidget {
  const NotificationRouteHandler({
    super.key,
    required this.router,
    required this.child,
  });

  final GoRouter router;
  final Widget child;

  @override
  ConsumerState<NotificationRouteHandler> createState() =>
      _NotificationRouteHandlerState();
}

class _NotificationRouteHandlerState
    extends ConsumerState<NotificationRouteHandler> {
  @override
  void initState() {
    super.initState();
    ref.listenManual(notificationTapsProvider, (_, next) {
      final route = next.valueOrNull;
      if (route != null && _location == kReminderRouteHome) _open(route);
    });
    unawaited(
      ref.read(notificationGatewayProvider).takeLaunchPayload().then((route) {
        if (route != null && mounted) _open(route);
      }),
    );
  }

  /// The top-most location, including pushed routes.
  String? get _location {
    if (widget.router.routerDelegate.currentConfiguration.isEmpty) return null;
    return widget.router.state.uri.path;
  }

  void _open(String route) {
    if (!kReminderRoutes.contains(route)) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      // Reminders only exist after onboarding; a stale tap otherwise does
      // nothing (the router keeps the player on onboarding).
      final onboarded =
          ref.read(appControllerProvider).valueOrNull?.onboarded ?? false;
      if (!onboarded) return;
      if (route == kReminderRouteHome) {
        widget.router.go(kReminderRouteHome);
      } else if (_location != route) {
        widget.router.go(kReminderRouteHome);
        widget.router.push(route);
      }
    });
    WidgetsBinding.instance.scheduleFrame();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
