import { Model, DataTypes } from 'sequelize';
import { sequelize } from '../config/database';

interface VideoAttributes {
  id: string;
  userId: string;
  filename: string;
  status: 'processing' | 'completed' | 'failed';
  prdDocument: string;
  businessPlan: string;
  createdAt: Date;
}

class Video extends Model<VideoAttributes> implements VideoAttributes {
  public id!: string;
  public userId!: string;
  public filename!: string;
  public status!: 'processing' | 'completed' | 'failed';
  public prdDocument!: string;
  public businessPlan!: string;
  public createdAt!: Date;
}

Video.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
      references: {
        model: 'Users',
        key: 'id',
      },
    },
    filename: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    status: {
      type: DataTypes.ENUM('processing', 'completed', 'failed'),
      defaultValue: 'processing',
      allowNull: false,
    },
    prdDocument: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    businessPlan: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    createdAt: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
      allowNull: false,
    },
  },
  {
    sequelize,
    modelName: 'Video',
    tableName: 'videos',
  }
);

export default Video;
