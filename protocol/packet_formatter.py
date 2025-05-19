import struct
import logging
from enum import IntEnum, unique

logger = logging.getLogger(__name__)

@unique
class CommandCode(IntEnum):
    MOVE = 0x01
    TURN = 0x02
    STOP = 0x03

class PacketFormatter:
    """
    Builds and parses command (ship->sub) and status (sub->ship) packets.

    CMD Packet Body (ship -> sub):
      - CommandCode:      1 byte
      - CommandParams:    2 bytes (signed)
      - MissingStatusCount: 1 byte
      - MissingStatusSeqs: N * 2 bytes
      - CRC-16:           2 bytes

    STATUS Packet Body (sub -> ship):
      - StatusCode:       1 byte
      - Depth:            2 bytes (unsigned)
      - Pressure:         2 bytes (unsigned)
      - MissingCmdCount:  1 byte
      - MissingCmdSeqs:   N * 2 bytes
      - X:                2 bytes (signed)
      - Y:                2 bytes (signed)
      - Z:                2 bytes (signed)
      - Heading:          2 bytes (signed)
      - CRC-16:           2 bytes
    """

    @staticmethod
    def _crc16(data: bytes) -> int:
        # Dummy CRC-16 placeholder; replace with real CRC
        return sum(data) & 0xFFFF

    @classmethod
    def build_cmd_packet(cls, cmd_code: CommandCode, param: int,
                         missing_status_seqs: list[int] = []) -> bytes:
        # '>B h B': 1-byte cmd, 2-byte signed param, 1-byte count
        body = struct.pack('>B h B', cmd_code, param, len(missing_status_seqs))
        for seq in missing_status_seqs:
            body += struct.pack('>H', seq)
        crc = cls._crc16(body)
        return body + struct.pack('>H', crc)

    @classmethod
    def parse_cmd_packet(cls, data: bytes) -> dict:
        header_fmt = '>B h B'
        header_size = struct.calcsize(header_fmt)
        cmd_code, param, miss_count = struct.unpack(header_fmt, data[:header_size])
        offset = header_size
        missing = []
        for _ in range(miss_count):
            seq, = struct.unpack('>H', data[offset:offset+2])
            missing.append(seq)
            offset += 2
        crc_recv, = struct.unpack('>H', data[offset:offset+2])
        crc_calc = cls._crc16(data[:offset])
        return {
            'command': CommandCode(cmd_code),
            'param': param,
            'missing_status_seqs': missing,
            'crc_valid': (crc_recv == crc_calc)
        }

    @classmethod
    def build_status_packet(cls, status: int, depth: int, pressure: int,
                            missing_cmd_seqs: list[int],
                            x: int, y: int, z: int, heading: int) -> bytes:
        # '>B H H B': status, depth, pressure, count
        body = struct.pack('>B H H B', status, depth, pressure, len(missing_cmd_seqs))
        for seq in missing_cmd_seqs:
            body += struct.pack('>H', seq)
        # '>h h h h': x, y, z, heading
        body += struct.pack('>h h h h', x, y, z, heading)
        crc = cls._crc16(body)
        return body + struct.pack('>H', crc)

    @classmethod
    def parse_status_packet(cls, data: bytes) -> dict:
        header_fmt = '>B H H B'
        header_size = struct.calcsize(header_fmt)
        status, depth, pressure, miss_count = struct.unpack(header_fmt, data[:header_size])
        offset = header_size
        missing = []
        for _ in range(miss_count):
            seq, = struct.unpack('>H', data[offset:offset+2])
            missing.append(seq)
            offset += 2
        x, y, z, heading = struct.unpack('>h h h h', data[offset:offset+8])
        offset += 8
        crc_recv, = struct.unpack('>H', data[offset:offset+2])
        crc_calc = cls._crc16(data[:offset])
        return {
            'status': status,
            'depth': depth,
            'pressure': pressure,
            'missing_cmd_seqs': missing,
            'position': (x, y, z),
            'heading': heading,
            'crc_valid': (crc_recv == crc_calc)
        }