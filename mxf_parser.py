"""
MXF文件解析模块
用于解析MXF (Material Exchange Format) 文件的结构和元数据
"""
import struct
import os
from typing import Dict, List, Tuple, Any


class MXFParser:
    """MXF文件解析器"""
    
    # MXF通用标签（UL - Universal Label）
    PARTITION_PACK = b'\x06\x0e\x2b\x34\x02\x05\x01\x01\x0d\x01\x02\x01\x01'
    HEADER_PARTITION = b'\x06\x0e\x2b\x34\x02\x05\x01\x01\x0d\x01\x02\x01\x01\x02'
    BODY_PARTITION = b'\x06\x0e\x2b\x34\x02\x05\x01\x01\x0d\x01\x02\x01\x01\x03'
    FOOTER_PARTITION = b'\x06\x0e\x2b\x34\x02\x05\x01\x01\x0d\x01\x02\x01\x01\x04'
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_size = os.path.getsize(filepath)
        self.partitions = []
        self.metadata = {}
        
    def parse(self) -> Dict[str, Any]:
        """解析MXF文件"""
        result = {
            'filepath': self.filepath,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2),
            'partitions': [],
            'metadata': {},
            'structure': []
        }
        
        try:
            with open(self.filepath, 'rb') as f:
                # 读取文件头
                header = f.read(16)
                
                # 检查是否为MXF文件
                if not self._is_mxf_file(header):
                    result['error'] = '不是有效的MXF文件'
                    return result
                
                # 解析分区
                f.seek(0)
                result['partitions'] = self._parse_partitions(f)
                
                # 解析基本元数据
                f.seek(0)
                result['metadata'] = self._parse_metadata(f)
                
                # 构建文件结构树
                result['structure'] = self._build_structure_tree(result['partitions'])
                
        except Exception as e:
            result['error'] = f'解析错误: {str(e)}'
            
        return result
    
    def _is_mxf_file(self, header: bytes) -> bool:
        """检查是否为MXF文件"""
        return header[:11] == b'\x06\x0e\x2b\x34\x02\x05\x01\x01\x0d\x01\x02'
    
    def _parse_partitions(self, f) -> List[Dict]:
        """解析分区信息"""
        partitions = []
        f.seek(0)
        
        while True:
            pos = f.tell()
            if pos >= self.file_size:
                break
                
            key = f.read(16)
            if len(key) < 16:
                break
            
            partition_type = self._identify_partition(key)
            if partition_type:
                length = self._read_ber_length(f)
                
                partition_info = {
                    'type': partition_type,
                    'offset': pos,
                    'offset_hex': hex(pos),
                    'key': key.hex(),
                    'length': length
                }
                
                # 读取并解析分区包内容
                if length > 0 and length < 10000:
                    content_start = f.tell()
                    content = f.read(length)
                    partition_info['content_preview'] = content[:64].hex()
                    
                    # 解析分区包详细信息
                    partition_details = self._parse_partition_pack(content)
                    partition_info.update(partition_details)
                
                partitions.append(partition_info)
            else:
                f.seek(pos + 1)
                
            if len(partitions) > 100 or pos > 10 * 1024 * 1024:
                break
        
        return partitions
    
    def _identify_partition(self, key: bytes) -> str:
        """识别分区类型"""
        if key[:14] == self.HEADER_PARTITION:
            return 'Header Partition'
        elif key[:14] == self.BODY_PARTITION:
            return 'Body Partition'
        elif key[:14] == self.FOOTER_PARTITION:
            return 'Footer Partition'
        elif key[:13] == self.PARTITION_PACK:
            return 'Generic Partition'
        return None
    
    def _read_ber_length(self, f) -> int:
        """读取BER编码的长度"""
        try:
            first_byte = f.read(1)[0]
            
            if first_byte < 128:
                return first_byte
            
            num_bytes = first_byte & 0x7F
            if num_bytes > 8:
                return 0
                
            length = 0
            for _ in range(num_bytes):
                length = (length << 8) | f.read(1)[0]
            
            return length
        except:
            return 0
    
    def _parse_partition_pack(self, content: bytes) -> Dict[str, Any]:
        """解析分区包的详细信息"""
        details = {}
        
        try:
            if len(content) < 88:  # 分区包最小长度
                return details
            
            # 解析主版本号和次版本号 (偏移0-1)
            major_version = struct.unpack('>H', content[0:2])[0]
            minor_version = struct.unpack('>H', content[2:4])[0]
            details['version'] = f"{major_version}.{minor_version}"
            
            # KAG大小 (偏移4-7)
            kag_size = struct.unpack('>I', content[4:8])[0]
            details['kag_size'] = kag_size
            details['kag_size_kb'] = round(kag_size / 1024, 2) if kag_size > 0 else 0
            
            # 本体偏移量 (偏移8-15)
            this_partition = struct.unpack('>Q', content[8:16])[0]
            details['this_partition'] = this_partition
            details['this_partition_hex'] = hex(this_partition)
            
            # 前一个分区偏移量 (偏移16-23)
            previous_partition = struct.unpack('>Q', content[16:24])[0]
            details['previous_partition'] = previous_partition
            details['previous_partition_hex'] = hex(previous_partition) if previous_partition > 0 else 'N/A'
            
            # Footer分区偏移量 (偏移24-31)
            footer_partition = struct.unpack('>Q', content[24:32])[0]
            details['footer_partition'] = footer_partition
            details['footer_partition_hex'] = hex(footer_partition) if footer_partition > 0 else 'N/A'
            
            # Header字节数 (偏移32-39)
            header_byte_count = struct.unpack('>Q', content[32:40])[0]
            details['header_byte_count'] = header_byte_count
            
            # Index字节数 (偏移40-47)
            index_byte_count = struct.unpack('>Q', content[40:48])[0]
            details['index_byte_count'] = index_byte_count
            
            # Index SID (偏移48-51)
            index_sid = struct.unpack('>I', content[48:52])[0]
            details['index_sid'] = index_sid
            
            # Body偏移量 (偏移52-59)
            body_offset = struct.unpack('>Q', content[52:60])[0]
            details['body_offset'] = body_offset
            details['body_offset_hex'] = hex(body_offset)
            
            # Body SID (偏移60-63)
            body_sid = struct.unpack('>I', content[60:64])[0]
            details['body_sid'] = body_sid
            
            # Operational Pattern (偏移64-79, 16字节UL)
            op_pattern = content[64:80]
            details['operational_pattern'] = op_pattern.hex()
            details['operational_pattern_name'] = self._identify_operational_pattern(op_pattern)
            
            # Essence Containers数量 (偏移80-83)
            if len(content) >= 84:
                essence_container_count = struct.unpack('>I', content[80:84])[0]
                details['essence_container_count'] = essence_container_count
                
                # 解析Essence Container标签
                if len(content) >= 84 + (essence_container_count * 16):
                    essence_containers = []
                    for i in range(essence_container_count):
                        start = 84 + (i * 16)
                        end = start + 16
                        ec_ul = content[start:end]
                        essence_containers.append({
                            'ul': ec_ul.hex(),
                            'name': self._identify_essence_container(ec_ul)
                        })
                    details['essence_containers'] = essence_containers
            
        except Exception as e:
            details['parse_error'] = str(e)
        
        return details
    
    def _identify_operational_pattern(self, op_pattern: bytes) -> str:
        """识别操作模式"""
        # SMPTE 377M定义的操作模式
        op_patterns = {
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x01\x01\x01\x00': 'OP1a',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x01\x01\x02\x00': 'OP1b',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x01\x01\x03\x00': 'OP1c',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x02\x01\x01\x00': 'OP2a',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x02\x01\x02\x00': 'OP2b',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x02\x01\x03\x00': 'OP2c',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x03\x01\x01\x00': 'OP3a',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x03\x01\x02\x00': 'OP3b',
            b'\x06\x0e\x2b\x34\x04\x01\x01\x01\x0d\x01\x02\x01\x03\x01\x03\x00': 'OP3c',
        }
        
        return op_patterns.get(op_pattern, 'Unknown')
    
    def _identify_essence_container(self, ec_ul: bytes) -> str:
        """识别本质容器类型"""
        # 常见的Essence Container类型
        if ec_ul[:13] == b'\x06\x0e\x2b\x34\x04\x01\x01':
            # DV essence
            if ec_ul[13:15] == b'\x01\x0d':
                return 'DV-Based Essence'
            # MPEG essence
            elif ec_ul[13:15] == b'\x02\x0d':
                return 'MPEG Elementary Stream'
            # Uncompressed picture
            elif ec_ul[13:15] == b'\x05\x0d':
                return 'Uncompressed Picture'
            # AES3/BWF audio
            elif ec_ul[13:15] == b'\x06\x0d':
                return 'AES3/BWF Audio'
            # JPEG 2000
            elif ec_ul[13:15] == b'\x0a\x0d':
                return 'JPEG 2000 Essence'
            # VC-3 (DNxHD)
            elif ec_ul[13:15] == b'\x11\x0d':
                return 'VC-3 (DNxHD) Essence'
        
        return 'Unknown Essence Container'
    
    def _parse_metadata(self, f) -> Dict:
        """解析元数据"""
        metadata = {}
        
        try:
            f.seek(0)
            header_data = f.read(1024)
            
            metadata['header_preview'] = header_data[:64].hex()
            
            if b'SMPTE' in header_data:
                metadata['standard'] = 'SMPTE'
            
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    def _build_structure_tree(self, partitions: List[Dict]) -> List[Dict]:
        """构建文件结构树"""
        structure = []
        
        for idx, partition in enumerate(partitions):
            node = {
                'id': f'partition_{idx}',
                'name': f"{partition['type']} @ {partition['offset_hex']}",
                'type': partition['type'],
                'offset': partition['offset'],
                'length': partition['length'],
                'children': []
            }
            structure.append(node)
        
        return structure
    
    def get_hex_dump(self, offset: int, length: int = 256) -> str:
        """获取指定位置的十六进制转储"""
        try:
            with open(self.filepath, 'rb') as f:
                f.seek(offset)
                data = f.read(length)
                
                hex_dump = []
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    hex_part = ' '.join(f'{b:02x}' for b in chunk)
                    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                    hex_dump.append(f'{offset+i:08x}  {hex_part:<48}  {ascii_part}')
                
                return '\n'.join(hex_dump)
        except Exception as e:
            return f'错误: {str(e)}'
