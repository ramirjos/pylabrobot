import unittest

from pylabrobot.liquid_handling.errors import (
  TipTooLittleLiquidError,
  TipTooLittleVolumeError,
  WellTooLittleLiquidError,
  WellTooLittleVolumeError
)
from pylabrobot.resources import Cos_96_EZWash, HTF_L
from pylabrobot.liquid_handling.standard import Aspiration, Dispense
from pylabrobot.liquid_handling.volume_tracker import TipVolumeTracker, WellVolumeTracker


class TestTipVolumeTracker(unittest.TestCase):
  """ Test for the tip volume tracker """

  def setUp(self) -> None:
    super().setUp()
    self.plate = Cos_96_EZWash("plate")
    self.tip_rack = HTF_L("tip")

  def test_init(self):
    tracker = TipVolumeTracker(max_volume=100)
    self.assertEqual(tracker.history, [])
    self.assertEqual(tracker.get_free_volume(), 100)
    self.assertEqual(tracker.get_used_volume(), 0)

    tracker.set_used_volume(volume=20)
    self.assertEqual(tracker.get_free_volume(), 80)
    self.assertEqual(tracker.get_used_volume(), 20)

  def test_aspirate(self):
    tracker = TipVolumeTracker(max_volume=100)

    op = Aspiration(resource=self.plate.get_item("A1"), volume=20, tip=self.tip_rack.get_tip("A1"))
    tracker.queue_op(op)
    self.assertEqual(tracker.history, [])
    self.assertEqual(tracker.get_used_volume(), 20)
    self.assertEqual(tracker.get_free_volume(), 80)

    tracker.commit()
    self.assertEqual(tracker.history, [op])
    self.assertEqual(tracker.get_used_volume(), 20)
    self.assertEqual(tracker.get_free_volume(), 80)

    op = Aspiration(resource=self.plate.get_item("A1"), volume=100, tip=self.tip_rack.get_tip("A1"))
    with self.assertRaises(TipTooLittleVolumeError):
      tracker.queue_op(op)

  def test_dispense(self):
    tracker = TipVolumeTracker(max_volume=100)

    asp = Aspiration(resource=self.plate.get_item("A1"), volume=80, tip=self.tip_rack.get_tip("A1"))
    tracker.queue_op(asp)

    disp = Dispense(resource=self.plate.get_item("A1"), volume=20, tip=self.tip_rack.get_tip("A1"))
    tracker.queue_op(disp)
    self.assertEqual(tracker.get_used_volume(), 60)
    self.assertEqual(tracker.get_free_volume(), 40)

    disp = Dispense(resource=self.plate.get_item("A1"), volume=100, tip=self.tip_rack.get_tip("A1"))
    with self.assertRaises(TipTooLittleLiquidError):
      tracker.queue_op(disp)


class TestWellVolumeTracker(unittest.TestCase):
  """ Test for the well volume tracker """

  def setUp(self) -> None:
    super().setUp()
    self.plate = Cos_96_EZWash("plate")
    self.tip_rack = HTF_L("tip")

  def test_init(self):
    tracker = WellVolumeTracker(max_volume=100)
    self.assertEqual(tracker.history, [])
    self.assertEqual(tracker.get_free_volume(), 100)
    self.assertEqual(tracker.get_used_volume(), 0)

    tracker.set_used_volume(volume=20)
    self.assertEqual(tracker.get_free_volume(), 80)
    self.assertEqual(tracker.get_used_volume(), 20)

  def test_aspirate(self):
    tracker = WellVolumeTracker(max_volume=100)

    op = Dispense(resource=self.plate.get_item("A1"), volume=20, tip=self.tip_rack.get_tip("A1"))
    tracker.queue_op(op)
    self.assertEqual(tracker.history, [])
    self.assertEqual(tracker.get_used_volume(), 20)
    self.assertEqual(tracker.get_free_volume(), 80)

    tracker.commit()
    self.assertEqual(tracker.history, [op])
    self.assertEqual(tracker.get_used_volume(), 20)
    self.assertEqual(tracker.get_free_volume(), 80)

    op = Dispense(resource=self.plate.get_item("A1"), volume=100, tip=self.tip_rack.get_tip("A1"))
    with self.assertRaises(WellTooLittleVolumeError):
      tracker.queue_op(op)

  def test_dispense(self):
    tracker = WellVolumeTracker(max_volume=100)

    disp = Dispense(resource=self.plate.get_item("A1"), volume=80, tip=self.tip_rack.get_tip("A1"))
    tracker.queue_op(disp)

    asp = Aspiration(resource=self.plate.get_item("A1"), volume=20, tip=self.tip_rack.get_tip("A1"))
    tracker.queue_op(asp)
    self.assertEqual(tracker.get_used_volume(), 60)
    self.assertEqual(tracker.get_free_volume(), 40)

    asp = Aspiration(resource=self.plate.get_item("A1"), volume=100,
      tip=self.tip_rack.get_tip("A1"))
    with self.assertRaises(WellTooLittleLiquidError):
      tracker.queue_op(asp)