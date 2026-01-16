
### Task LD

```python
reservationId = conveyor.ReserveFreePalletOfType2(
    num of pallets, c1, c2, c3, type
)

out <- reservationId
```

### Task RBTC

```python
reservationId -> in
istr 0: Tray = {target: Warehosue, node: extract}

istr 1: Tray == 10:
            istr 0

istr 2: Tray == 1:
        istr 3
        else
        istr 1

istr 3: Mobile Robot ....           

conveyor.call_resrved_pallet(reservationId,  dest = Cell4)
Wait conveyor.variable( = Cell4) == Pallet
shape1 = conveyor.read(${Pallet}.content_2)
bufferPos = cell4.pick_part_on_pallet(pos=2)
conveyor.write(${Pallet}.content_2, 0)
conveyor.releasePallet(Pallet)
conveyor.setPalletDestination(Pallet, 0)

Pallet = conveyor.call_resrved_pallet(reservationId,  dest = Cell4)
Wait conveyor.variable( = Cell4) == Pallet
shape2 = conveyor.read(${Pallet}.content_2)
cell4.move_content(from_pos=2, to_pos=3)

conveyor.write(${Pallet}.content_2, 0)
conveyor.write(${Pallet}.content_3, ${shape2})

cell4.place_from_buffer(bufferPos, to_pos=1)

conveyor.write(${Pallet}.content_1, ${shape1})
conveyor.setPalletDestination(Pallet, 0)


out <- Pallet, shape1, shape2
```

### Task QC
```
Pallet, shape1, shape2 -> in

conveyor.setPalletDestinatio(Pallet, dest=QC)
Wait conveyor.variable(dest = QC) == Pallet
cell5.check_lego(s1=shape1, s2=0, s3=shape2)
conveyor.setPalletDestination(Pallet, 0)

```

### Task DISASSEMBLE after QC

```
Pallet, shape1, shape2 -> in

conveyor.setPalletDestination(Pallet, dest = Cell4)
Wait conveyor.variable( = Cell4) == Pallet
bufferPos = cell4.pick_part_on_pallet(pos=1)
conveyor.write(${Pallet}.content_1, 0)
cell4.move_content(from_pos=3, to_pos=2)
conveyor.write(${Pallet}.content_2, ${shape2})
conveyor.release(Pallet)
conveyor.setPalletDestination(Pallet, 0)

out <- bufferPos
```

### Task RESERVE after QC


```python
reservationId = conveyor.ReserveFreePalletOfType2(
    1, c1=0, c2=0, c3=0, type
)

out <- reservationId
```


### Task PUT_BACK after DISASSEMBLE, RESERVE

```
reservationId, shape1, bufferPos -> in

Pallet = conveyor.call_resrved_pallet(reservationId,  dest = Cell4)
Wait conveyor.variable( = Cell4) == Pallet

cell4.place_on_pallet(bufferPos, to_pos=2)
conveyor.write(${Pallet}.content_2, ${shape1})
conveyor.release(Pallet)
conveyor.setPalletDestination(Pallet, 0)
```